import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.session import Base


class MLModelRegistry(Base):
    __tablename__ = "ml_model_registry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)

    model_name = Column(String(128), nullable=False)  # e.g. "churn_random_forest"
    model_type = Column(String(64), nullable=False)  # "classification" | "regression"
    version = Column(String(64), nullable=False)

    mlflow_run_id = Column(String(64), nullable=True)
    mlflow_experiment_id = Column(String(64), nullable=True)
    artifact_path = Column(String(1024), nullable=False)

    metrics_json = Column(Text, nullable=True)
    params_json = Column(Text, nullable=True)

    trained_at = Column(DateTime(timezone=True), server_default=func.now())
