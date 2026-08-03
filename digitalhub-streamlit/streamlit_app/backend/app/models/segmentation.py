import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    recency_days = Column(Integer, nullable=False)
    frequency = Column(Integer, nullable=False)
    monetary = Column(Float, nullable=False)

    r_score = Column(Integer, nullable=False)
    f_score = Column(Integer, nullable=False)
    m_score = Column(Integer, nullable=False)
    rfm_score = Column(String(8), nullable=False)  # e.g. "455"

    segment_label = Column(String(64), nullable=False)  # Champions, Loyal, At Risk, ...

    computed_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="segment")
