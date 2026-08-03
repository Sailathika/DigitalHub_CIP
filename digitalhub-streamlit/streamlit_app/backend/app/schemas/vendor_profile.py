import uuid

from pydantic import BaseModel, Field


class VendorProfileOut(BaseModel):
    id: uuid.UUID
    business_name: str | None = None
    owner_name: str
    email: str
    phone: str | None = None
    gst_number: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None


class VendorProfileUpdateRequest(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    owner_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=5, max_length=32)
    gst_number: str | None = Field(None, max_length=32)
    address: str = Field(..., min_length=1, max_length=512)
    city: str = Field(..., min_length=1, max_length=128)
    state: str = Field(..., min_length=1, max_length=128)
