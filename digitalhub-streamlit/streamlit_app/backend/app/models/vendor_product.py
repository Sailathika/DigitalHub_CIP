import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class VendorProductStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class VendorProduct(Base):
    """A vendor's own product catalog entry, managed from the My Products
    page. Distinct from `app.models.product.Product`, which holds
    dataset-derived sales analytics rows loaded by the ETL pipeline."""

    __tablename__ = "vendor_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    category = Column(String(128), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, nullable=False, default=0)
    sku = Column(String(64), nullable=False, index=True)
    brand = Column(String(128), nullable=True)
    image_path = Column(String(1024), nullable=True)
    status = Column(Enum(VendorProductStatus), nullable=False, default=VendorProductStatus.ACTIVE)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    vendor = relationship("User")
