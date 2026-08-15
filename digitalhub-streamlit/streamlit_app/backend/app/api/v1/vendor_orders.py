import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_vendor
from app.database.session import get_db
from app.models.user import User
from app.schemas.vendor_order import (
    VendorOrderListResponse,
    VendorOrderOut,
)
from app.services.vendor_order_service import VendorOrderService


router = APIRouter(
    prefix="/vendor/orders",
    tags=["Vendor Orders"],
)


@router.get(
    "/",
    response_model=VendorOrderListResponse,
)
def list_vendor_orders(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vendor),
):
    return VendorOrderService(db).list_orders(
        vendor_id=current_user.id,
        search=search,
        status=status_filter,
    )


@router.get(
    "/{order_id}",
    response_model=VendorOrderOut,
)
def get_vendor_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vendor),
):
    try:
        return VendorOrderService(db).get_order(
            vendor_id=current_user.id,
            order_id=order_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )