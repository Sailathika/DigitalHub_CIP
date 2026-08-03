import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.session import Base


class ETLStage(str, enum.Enum):
    EXTRACT = "extract"
    VALIDATE = "validate"
    CLEAN = "clean"
    TRANSFORM = "transform"
    LOAD = "load"


class ETLStatus(str, enum.Enum):
    SUCCESS = "success"
    WARNING = "warning"
    FAILED = "failed"


class ETLLog(Base):
    __tablename__ = "etl_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)

    stage = Column(Enum(ETLStage), nullable=False)
    status = Column(Enum(ETLStatus), nullable=False)
    message = Column(Text, nullable=True)

    rows_before = Column(Integer, nullable=True)
    rows_after = Column(Integer, nullable=True)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
