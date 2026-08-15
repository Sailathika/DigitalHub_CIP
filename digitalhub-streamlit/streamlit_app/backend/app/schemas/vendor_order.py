import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.order import OrderStatus


class VendorOrderCustomer(BaseModel):
    id: uuid.UUID
    name: str
    email: Optional[str] = None


class VendorOrderProduct(BaseModel):
    id: uuid.UUID
    name: Optional[str] = None
    category: Optional[str] = None
    product_ref: Optional[str] = None


class VendorOrderOut(BaseModel):
    id: uuid.UUID
    order_ref: Optional[str] = None
    order_date: datetime
    quantity: int
    amount: float
    status: OrderStatus

    customer: Optional[VendorOrderCustomer] = None
    product: Optional[VendorOrderProduct] = None

    model_config = ConfigDict(from_attributes=True)


class VendorOrderListResponse(BaseModel):
    orders: list[VendorOrderOut]
    total: int