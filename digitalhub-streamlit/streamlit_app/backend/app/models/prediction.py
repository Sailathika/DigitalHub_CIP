import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.session import Base


class CLVPrediction(Base):
    __tablename__ = "clv_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)

    predicted_clv = Column(Float, nullable=False)
    model_version = Column(String(64), nullable=False)
    mlflow_run_id = Column(String(64), nullable=True)

    predicted_at = Column(DateTime(timezone=True), server_default=func.now())


class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)

    churn_probability = Column(Float, nullable=False)
    risk_level = Column(String(16), nullable=False)  # Low | Medium | High
    model_version = Column(String(64), nullable=False)
    mlflow_run_id = Column(String(64), nullable=True)
    feature_importance_json = Column(Text, nullable=True)

    predicted_at = Column(DateTime(timezone=True), server_default=func.now())
