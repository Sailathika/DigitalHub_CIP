import uuid
from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from app.ml.rfm import compute_rfm
from app.models.segmentation import CustomerSegment
from app.repository.customer_repository import CustomerRepository
from app.repository.prediction_repository import SegmentationRepository
from app.schemas.prediction import RFMRecord, RFMResponse, SegmentDistribution
from app.services.analytics_service import _customers_to_frame, build_rfm_feature_frame
from app.utils.response_utils import get_dataset_or_404


class SegmentationService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.segment_repo = SegmentationRepository(db)

    def compute_rfm_segmentation(self, dataset_id: uuid.UUID) -> RFMResponse:
        get_dataset_or_404(self.db, dataset_id)
        customers = self.customer_repo.list_by_dataset(dataset_id)
        if not customers:
            raise ValueError("No customers loaded for this dataset. Run the ETL pipeline first.")

        df = build_rfm_feature_frame(_customers_to_frame(customers))
        rfm_df = compute_rfm(df)

        # Persist — clear any prior segmentation for this dataset first.
        self.segment_repo.delete_by_dataset(dataset_id)
        segment_rows = [
            CustomerSegment(
                dataset_id=dataset_id,
                customer_id=row["id"],
                recency_days=int(row["recency_days"]),
                frequency=int(row["frequency"]),
                monetary=float(row["monetary"]),
                r_score=int(row["r_score"]),
                f_score=int(row["f_score"]),
                m_score=int(row["m_score"]),
                rfm_score=str(row["rfm_score"]),
                segment_label=str(row["segment_label"]),
            )
            for _, row in rfm_df.iterrows()
        ]
        self.segment_repo.bulk_create(segment_rows)

        records = [
            RFMRecord(
                customer_id=row["id"],
                customer_ref=row["customer_ref"],
                name=row["name"] or row["customer_ref"],
                recency_days=int(row["recency_days"]),
                frequency=int(row["frequency"]),
                monetary=float(row["monetary"]),
                r_score=int(row["r_score"]),
                f_score=int(row["f_score"]),
                m_score=int(row["m_score"]),
                rfm_score=str(row["rfm_score"]),
                segment_label=str(row["segment_label"]),
            )
            for _, row in rfm_df.iterrows()
        ]

        distribution_df = rfm_df.groupby("segment_label").agg(
            customer_count=("customer_ref", "count"), total_monetary=("monetary", "sum")
        ).reset_index()
        distribution = [
            SegmentDistribution(
                segment_label=row["segment_label"],
                customer_count=int(row["customer_count"]),
                total_monetary=round(float(row["total_monetary"]), 2),
            )
            for _, row in distribution_df.iterrows()
        ]

        return RFMResponse(dataset_id=dataset_id, records=records, distribution=distribution)

    def get_segmentation(self, dataset_id: uuid.UUID) -> RFMResponse:
        get_dataset_or_404(self.db, dataset_id)
        segments: List[CustomerSegment] = self.segment_repo.list_by_dataset(dataset_id)
        if not segments:
            raise ValueError("Segmentation has not been computed for this dataset yet.")

        records = [
            RFMRecord(
                customer_id=s.customer_id,
                customer_ref=s.customer.customer_ref,
                name=s.customer.name or s.customer.customer_ref,
                recency_days=s.recency_days,
                frequency=s.frequency,
                monetary=s.monetary,
                r_score=s.r_score,
                f_score=s.f_score,
                m_score=s.m_score,
                rfm_score=s.rfm_score,
                segment_label=s.segment_label,
            )
            for s in segments
        ]
        df = pd.DataFrame([{"segment_label": s.segment_label, "monetary": s.monetary} for s in segments])
        distribution_df = df.groupby("segment_label").agg(
            customer_count=("monetary", "count"), total_monetary=("monetary", "sum")
        ).reset_index()
        distribution = [
            SegmentDistribution(
                segment_label=row["segment_label"],
                customer_count=int(row["customer_count"]),
                total_monetary=round(float(row["total_monetary"]), 2),
            )
            for _, row in distribution_df.iterrows()
        ]
        return RFMResponse(dataset_id=dataset_id, records=records, distribution=distribution)
