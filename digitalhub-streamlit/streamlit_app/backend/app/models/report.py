import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.session import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(String(512), nullable=True)
    report_type = Column(String(64), nullable=False, default="full_analytics")
    file_path = Column(String(1024), nullable=False)

    generated_by = Column(UUID(as_uuid=True), nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
