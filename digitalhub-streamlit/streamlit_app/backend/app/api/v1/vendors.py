import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.vendor import (
    VendorCommissionUpdateRequest,
    VendorCreateRequest,
    VendorDetailResponse,
    VendorListResponse,
    VendorOut,
    VendorStatusUpdateRequest,
    VendorUpdateRequest,
)
from app.services.vendor_service import VENDOR_CATEGORIES, VendorService

router = APIRouter(prefix="/vendors", tags=["Vendor Management"])


@router.get("/", response_model=VendorListResponse)
def list_vendors(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    vendors = VendorService(db).list_vendors(search=search, status_filter=status_filter, category=category)
    return VendorListResponse(
        vendors=vendors,
        categories=VENDOR_CATEGORIES,
        statuses=["pending", "active", "suspended"],
    )


@router.post("/", response_model=VendorOut, status_code=status.HTTP_201_CREATED)
def create_vendor(payload: VendorCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return VendorService(db).create_vendor(payload)


@router.get("/{vendor_id}", response_model=VendorDetailResponse)
def get_vendor_detail(vendor_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return VendorService(db).get_vendor_detail(vendor_id)


@router.put("/{vendor_id}", response_model=VendorOut)
def update_vendor(
    vendor_id: uuid.UUID,
    payload: VendorUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return VendorService(db).update_vendor(vendor_id, payload)


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendor(vendor_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    VendorService(db).delete_vendor(vendor_id)
    return None


@router.patch("/{vendor_id}/status", response_model=VendorOut)
def update_vendor_status(
    vendor_id: uuid.UUID,
    payload: VendorStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return VendorService(db).update_status(vendor_id, payload)


@router.post("/{vendor_id}/approve", response_model=VendorOut)
def approve_vendor(vendor_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return VendorService(db).approve_vendor(vendor_id)


@router.post("/{vendor_id}/suspend", response_model=VendorOut)
def suspend_vendor(vendor_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return VendorService(db).suspend_vendor(vendor_id)


@router.post("/{vendor_id}/activate", response_model=VendorOut)
def activate_vendor(vendor_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return VendorService(db).activate_vendor(vendor_id)


@router.patch("/{vendor_id}/commission", response_model=VendorOut)
def update_commission(
    vendor_id: uuid.UUID,
    payload: VendorCommissionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return VendorService(db).update_commission(vendor_id, payload)
