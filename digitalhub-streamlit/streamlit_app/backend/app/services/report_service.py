import uuid
from pathlib import Path
from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from app.config import settings
from app.models.report import Report
from app.repository.base import BaseRepository
from app.repository.customer_repository import CustomerRepository, OrderRepository, ProductRepository
from app.repository.dataset_repository import DatasetRepository
from app.repository.prediction_repository import CLVRepository, ChurnRepository, SegmentationRepository
from app.reports.pdf_builder import build_report
from app.schemas.report import ReportGenerateRequest
from app.services.analytics_service import AnalyticsService
from app.services.churn_service import ChurnService
from app.services.clv_service import CLVService
from app.services.segmentation_service import SegmentationService
from app.utils.logger import get_logger
from app.utils.response_utils import get_dataset_or_404

logger = get_logger(__name__)


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.datasets = DatasetRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.order_repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)
        self.reports = BaseRepository(db, Report)
        self.segment_repo = SegmentationRepository(db)
        self.clv_repo = CLVRepository(db)
        self.churn_repo = ChurnRepository(db)
        self.analytics = AnalyticsService(db)
        self.segmentation = SegmentationService(db)
        self.clv = CLVService(db)
        self.churn = ChurnService(db)

    def list_reports(self, dataset_id: uuid.UUID = None) -> List[Report]:
        query = self.db.query(Report)
        if dataset_id:
            query = query.filter(Report.dataset_id == dataset_id)
        return query.order_by(Report.generated_at.desc()).all()

    def generate(self, dataset_id: uuid.UUID, options: ReportGenerateRequest, generated_by: uuid.UUID = None) -> Report:
        dataset = get_dataset_or_404(self.db, dataset_id)
        customers = self.customer_repo.list_by_dataset(dataset_id)
        orders = self.order_repo.list_by_dataset(dataset_id)
        products = self.product_repo.list_by_dataset(dataset_id)

        total_revenue = sum(o.amount for o in orders)
        avg_order_value = (total_revenue / len(orders)) if orders else 0

        sections = {
            "executive_summary": (
                f"This report summarizes marketplace performance for '{dataset.original_filename}', "
                f"covering {len(customers)} customers across {len(orders)} orders and {len(products)} products. "
                f"Total revenue in the dataset is Rs. {total_revenue:,.0f}."
            ),
            "dataset_summary": {
                "row_count": dataset.row_count,
                "column_count": dataset.column_count,
                "file_type": dataset.file_type,
                "status": dataset.status.value if hasattr(dataset.status, "value") else dataset.status,
            },
            "eda_summary": {
                "total_revenue": total_revenue,
                "total_orders": len(orders),
                "total_customers": len(customers),
                "total_products": len(products),
                "average_order_value": avg_order_value,
            },
        }

        try:
            overview = self.analytics.customer_overview(dataset_id)
            sales = self.analytics.sales_analytics(dataset_id)
            sections["customer_analytics"] = {
                "total_customers": overview.total_customers,
                "returning_customers": overview.returning_customers,
                "active_customers": overview.active_customers,
                "average_order_value": overview.average_order_value,
                "sales_trend": [t.model_dump() for t in sales.sales_trend],
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipping customer analytics section: %s", exc)

        if options.include_segmentation:
            rfm = None
            try:
                rfm = self.segmentation.get_segmentation(dataset_id)
            except ValueError:
                try:
                    rfm = self.segmentation.compute_rfm_segmentation(dataset_id)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Skipping segmentation section: %s", exc)
            if rfm:
                sections["segmentation"] = {"distribution": [d.model_dump() for d in rfm.distribution]}

        if options.include_clv:
            try:
                clv_result = self.clv.predict(dataset_id)
                sections["clv"] = {
                    "model_version": clv_result.model_version,
                    "r2_score": None,
                    "mae": None,
                    "top_predictions": [p.model_dump() for p in clv_result.predictions[:10]],
                }
            except Exception as exc:  # noqa: BLE001
                logger.warning("Skipping CLV section: %s", exc)

        if options.include_churn:
            try:
                churn_result = self.churn.predict(dataset_id)
                sections["churn"] = {
                    "model_version": churn_result.model_version,
                    "accuracy": None,
                    "f1_score": None,
                    "feature_importance": churn_result.feature_importance,
                    "predictions": [p.model_dump() for p in churn_result.predictions],
                }
            except Exception as exc:  # noqa: BLE001
                logger.warning("Skipping churn section: %s", exc)

        if options.include_recommendations and products:
            top_products = sorted(products, key=lambda p: p.total_revenue, reverse=True)[:10]
            sections["recommendations"] = {
                "top_recommended": [
                    {"name": p.name, "category": p.category or "Uncategorized", "score": 1.0} for p in top_products
                ]
            }

        report_id = uuid.uuid4()
        output_path = settings.REPORTS_DIR / f"{report_id}.pdf"
        build_report(output_path, dataset.original_filename, sections)

        report = self.reports.create(
            id=report_id,
            dataset_id=dataset_id,
            name=f"Analytics Report - {dataset.original_filename}",
            description="Full marketplace analytics report including customer, segmentation, CLV, churn, and recommendation insights.",
            report_type="full_analytics",
            file_path=str(output_path),
            generated_by=generated_by,
        )
        return report

    def export_customers_csv(self, dataset_id: uuid.UUID) -> Path:
        """Export customer-level data (with segment/CLV/churn results, when
        available) as CSV — the "CSV report" alongside the PDF report."""
        get_dataset_or_404(self.db, dataset_id)
        customers = self.customer_repo.list_by_dataset(dataset_id)

        segments = {s.customer_id: s for s in self.segment_repo.list_by_dataset(dataset_id)}
        clv_predictions = {p.customer_id: p for p in self.clv_repo.list_by_dataset(dataset_id)}
        churn_predictions = {p.customer_id: p for p in self.churn_repo.list_by_dataset(dataset_id)}

        rows = []
        for customer in customers:
            segment = segments.get(customer.id)
            clv = clv_predictions.get(customer.id)
            churn = churn_predictions.get(customer.id)
            rows.append(
                {
                    "customer_id": customer.customer_ref,
                    "name": customer.name,
                    "email": customer.email,
                    "total_orders": customer.total_orders,
                    "total_spent": customer.total_spent,
                    "avg_order_value": customer.avg_order_value,
                    "first_purchase_date": customer.first_purchase_date,
                    "last_purchase_date": customer.last_purchase_date,
                    "rfm_segment": segment.segment_label if segment else None,
                    "rfm_score": segment.rfm_score if segment else None,
                    "predicted_clv": clv.predicted_clv if clv else None,
                    "churn_probability": churn.churn_probability if churn else None,
                    "churn_risk": churn.risk_level if churn else None,
                }
            )

        df = pd.DataFrame(rows)
        output_path = settings.REPORTS_DIR / f"customers_{dataset_id}.csv"
        df.to_csv(output_path, index=False)
        return output_path
