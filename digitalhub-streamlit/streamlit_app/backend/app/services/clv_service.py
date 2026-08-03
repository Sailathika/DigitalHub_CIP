import json
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.ml.clv_model import load_clv_model, predict_clv, train_clv_model
from app.models.ml_model import MLModelRegistry
from app.models.prediction import CLVPrediction
from app.repository.base import BaseRepository
from app.repository.customer_repository import CustomerRepository
from app.repository.prediction_repository import CLVRepository
from app.schemas.prediction import CLVPredictionRecord, CLVPredictResponse, CLVTrainResponse
from app.services.analytics_service import _customers_to_frame, build_rfm_feature_frame
from app.utils.response_utils import get_dataset_or_404


class CLVService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.clv_repo = CLVRepository(db)
        self.model_registry = BaseRepository(db, MLModelRegistry)

    def train(self, dataset_id: uuid.UUID) -> CLVTrainResponse:
        get_dataset_or_404(self.db, dataset_id)
        customers = self.customer_repo.list_by_dataset(dataset_id)
        df = build_rfm_feature_frame(_customers_to_frame(customers))

        model, metrics, run_id, artifact_path = train_clv_model(df, dataset_id)

        self.model_registry.create(
            dataset_id=dataset_id,
            model_name="clv_gradient_boosting",
            model_type="regression",
            version=artifact_path.stem,
            mlflow_run_id=run_id,
            artifact_path=str(artifact_path),
            metrics_json=json.dumps(metrics),
            params_json=json.dumps({"n_estimators": 200, "learning_rate": 0.05, "max_depth": 3}),
        )

        return CLVTrainResponse(
            dataset_id=dataset_id,
            model_version=artifact_path.stem,
            mlflow_run_id=run_id,
            r2_score=metrics["r2_score"],
            mae=metrics["mae"],
            trained_on_customers=len(df),
        )

    def predict(self, dataset_id: uuid.UUID) -> CLVPredictResponse:
        get_dataset_or_404(self.db, dataset_id)
        latest_model = (
            self.db.query(MLModelRegistry)
            .filter(MLModelRegistry.dataset_id == dataset_id, MLModelRegistry.model_name == "clv_gradient_boosting")
            .order_by(MLModelRegistry.trained_at.desc())
            .first()
        )
        if latest_model is None:
            raise ValueError("No trained CLV model found for this dataset. Train one first.")

        customers = self.customer_repo.list_by_dataset(dataset_id)
        df = build_rfm_feature_frame(_customers_to_frame(customers))

        model = load_clv_model(Path(latest_model.artifact_path))
        predictions = predict_clv(model, df)
        df = df.assign(predicted_clv=predictions)

        self.clv_repo.delete_by_dataset(dataset_id)
        rows = [
            CLVPrediction(
                dataset_id=dataset_id,
                customer_id=row["id"],
                predicted_clv=float(row["predicted_clv"]),
                model_version=latest_model.version,
                mlflow_run_id=latest_model.mlflow_run_id,
            )
            for _, row in df.iterrows()
        ]
        self.clv_repo.bulk_create(rows)

        records = sorted(
            [
                CLVPredictionRecord(
                    customer_id=row["id"],
                    customer_ref=row["customer_ref"],
                    name=row["name"] or row["customer_ref"],
                    predicted_clv=round(float(row["predicted_clv"]), 2),
                )
                for _, row in df.iterrows()
            ],
            key=lambda r: r.predicted_clv,
            reverse=True,
        )

        return CLVPredictResponse(dataset_id=dataset_id, model_version=latest_model.version, predictions=records)
