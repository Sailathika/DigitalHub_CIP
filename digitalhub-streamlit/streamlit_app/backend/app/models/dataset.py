import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.session import Base


class DatasetStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    VALIDATED = "validated"
    CLEANED = "cleaned"
    TRANSFORMED = "transformed"
    FAILED = "failed"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String(512), nullable=False)
    stored_filename = Column(String(512), nullable=False)
    file_path = Column(String(1024), nullable=False)
    cleaned_file_path = Column(String(1024), nullable=True)
    file_type = Column(String(16), nullable=False)  # csv | xlsx | xls

    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)

    status = Column(Enum(DatasetStatus), nullable=False, default=DatasetStatus.UPLOADED)

    uploaded_by = Column(UUID(as_uuid=True), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
