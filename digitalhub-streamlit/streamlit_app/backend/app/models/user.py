import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.session import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    VENDOR = "vendor"


class VendorStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VENDOR)

    # Vendor-specific profile fields (null for admins)
    business_name = Column(String(255), nullable=True)
    phone = Column(String(32), nullable=True)
    address = Column(String(512), nullable=True)
    city = Column(String(128), nullable=True)
    state = Column(String(128), nullable=True)
    category = Column(String(128), nullable=True)
    gst_number = Column(String(32), nullable=True)

    # Vendor management (admin-controlled)
    vendor_status = Column(Enum(VendorStatus), nullable=False, default=VendorStatus.PENDING)
    commission_percent = Column(Float, nullable=False, default=10.0)
    rating = Column(Float, nullable=False, default=0.0)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

