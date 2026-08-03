import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.session import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)

    # Original identifier/name as they appeared in the uploaded file
    customer_ref = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)

    first_purchase_date = Column(DateTime(timezone=True), nullable=True)
    last_purchase_date = Column(DateTime(timezone=True), nullable=True)

    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    avg_order_value = Column(Float, default=0.0)

    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    segment = relationship("CustomerSegment", back_populates="customer", uselist=False, cascade="all, delete-orphan")
