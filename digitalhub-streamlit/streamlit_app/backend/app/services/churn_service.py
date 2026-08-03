import json
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.ml.churn_model import load_churn_model, predict_churn, risk_level, train_churn_model
from app.models.ml_model import MLModelRegistry
from app.models.prediction import ChurnPrediction
from app.repository.base import BaseRepository
from app.repository.customer_repository import CustomerRepository
from app.repository.prediction_repository import ChurnRepository
from app.schemas.prediction import ChurnPredictionRecord, ChurnPredictResponse, ChurnTrainResponse
from app.services.analytics_service import _customers_to_frame, build_rfm_feature_frame
from app.utils.response_utils import get_dataset_or_404


class ChurnService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.churn_repo = ChurnRepository(db)
        self.model_registry = BaseRepository(db, MLModelRegistry)

    def train(self, dataset_id: uuid.UUID) -> ChurnTrainResponse:
        get_dataset_or_404(self.db, dataset_id)
        customers = self.customer_repo.list_by_dataset(dataset_id)
        df = build_rfm_feature_frame(_customers_to_frame(customers))

        model, metrics, run_id, artifact_path = train_churn_model(df, dataset_id)

        self.model_registry.create(
            dataset_id=dataset_id,
            model_name="churn_random_forest",
            model_type="classification",
            version=artifact_path.stem,
            mlflow_run_id=run_id,
            artifact_path=str(artifact_path),
            metrics_json=json.dumps({k: v for k, v in metrics.items() if k != "feature_importance"}),
            params_json=json.dumps({"n_estimators": 300, "max_depth": 6, "min_samples_leaf": 2}),
        )

        return ChurnTrainResponse(
            dataset_id=dataset_id,
            model_version=artifact_path.stem,
            mlflow_run_id=run_id,
            accuracy=metrics["accuracy"],
            precision=metrics["precision"],
            recall=metrics["recall"],
            f1_score=metrics["f1_score"],
            feature_importance=metrics["feature_importance"],
            trained_on_customers=len(df),
        )

    def predict(self, dataset_id: uuid.UUID) -> ChurnPredictResponse:
        get_dataset_or_404(self.db, dataset_id)
        latest_model = (
            self.db.query(MLModelRegistry)
            .filter(MLModelRegistry.dataset_id == dataset_id, MLModelRegistry.model_name == "churn_random_forest")
            .order_by(MLModelRegistry.trained_at.desc())
            .first()
        )
        if latest_model is None:
            raise ValueError("No trained churn model found for this dataset. Train one first.")

        customers = self.customer_repo.list_by_dataset(dataset_id)
        df = build_rfm_feature_frame(_customers_to_frame(customers))

        model = load_churn_model(Path(latest_model.artifact_path))
        probabilities = predict_churn(model, df)
        df = df.assign(churn_probability=probabilities)

        self.churn_repo.delete_by_dataset(dataset_id)
        feature_importance = {}
        try:
            from app.ml.churn_model import FEATURE_COLUMNS

            feature_importance = dict(zip(FEATURE_COLUMNS, model.feature_importances_.tolist()))
        except Exception:  # noqa: BLE001
            pass

        rows = [
            ChurnPrediction(
                dataset_id=dataset_id,
                customer_id=row["id"],
                churn_probability=float(row["churn_probability"]),
                risk_level=risk_level(float(row["churn_probability"])),
                model_version=latest_model.version,
                mlflow_run_id=latest_model.mlflow_run_id,
                feature_importance_json=json.dumps(feature_importance),
            )
            for _, row in df.iterrows()
        ]
        self.churn_repo.bulk_create(rows)

        records = sorted(
            [
                ChurnPredictionRecord(
                    customer_id=row["id"],
                    customer_ref=row["customer_ref"],
                    name=row["name"] or row["customer_ref"],
                    churn_probability=round(float(row["churn_probability"]), 4),
                    risk_level=risk_level(float(row["churn_probability"])),
                )
                for _, row in df.iterrows()
            ],
            key=lambda r: r.churn_probability,
            reverse=True,
        )

        return ChurnPredictResponse(
            dataset_id=dataset_id,
            model_version=latest_model.version,
            predictions=records,
            feature_importance={k: round(v, 4) for k, v in feature_importance.items()},
        )
