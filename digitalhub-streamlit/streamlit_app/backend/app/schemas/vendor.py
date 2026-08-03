import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class VendorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_name: Optional[str] = None
    full_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    gst_number: Optional[str] = None
    vendor_status: str
    commission_percent: float
    rating: float
    is_active: bool
    created_at: datetime


class VendorListResponse(BaseModel):
    vendors: List[VendorOut]
    categories: List[str]
    statuses: List[str]


class VendorCreateRequest(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    owner_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=5, max_length=32)
    address: str = Field(..., min_length=1, max_length=512)
    category: Optional[str] = None
    gst_number: Optional[str] = None
    commission_percent: float = 10.0
    password: str = Field(..., min_length=8, max_length=128)


class VendorUpdateRequest(BaseModel):
    business_name: Optional[str] = None
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    gst_number: Optional[str] = None


class VendorCommissionUpdateRequest(BaseModel):
    commission_percent: float = Field(..., ge=0, le=100)


class VendorStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(pending|active|suspended)$")


class RecentActivityItem(BaseModel):
    label: str
    timestamp: datetime


class VendorDetailResponse(BaseModel):
    vendor: VendorOut
    total_products: int
    total_orders: int
    total_revenue: float
    sales_trend: List[dict]
    top_products: List[dict]
    recent_orders: List[dict]
    recent_activity: List[RecentActivityItem]
