import uuid

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.session import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    product_ref = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    category = Column(String(255), nullable=True)

    total_units_sold = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    stock_quantity = Column(Integer, nullable=True)

    orders = relationship("Order", back_populates="product")

