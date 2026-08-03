import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VendorProductInput(BaseModel):
    """Validates the assembled product data (from multipart Form fields)
    before it's written to the database, for both create and update."""

    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    sku: str = Field(..., min_length=1, max_length=64)
    brand: Optional[str] = Field(None, max_length=128)
    status: str = Field("active", pattern="^(active|inactive|draft)$")

    @field_validator("name", "sku")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("This field cannot be blank")
        return value.strip()


class VendorProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    price: float
    stock: int
    sku: str
    brand: Optional[str] = None
    image_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class VendorProductListResponse(BaseModel):
    products: List[VendorProductOut]
    categories: List[str]


class VendorInventoryResponse(BaseModel):
    total_products: int
    in_stock: int
    low_stock: int
    out_of_stock: int
    total_inventory_value: float
    low_stock_threshold: int
    products: List[VendorProductOut]
