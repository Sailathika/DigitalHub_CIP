from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_vendor
from app.database.session import get_db
from app.models.user import User
from app.services.vendor_sales_service import VendorSalesService

router = APIRouter(prefix="/vendor/sales-analytics", tags=["Vendor Sales Analytics"])


@router.get("")
def get_vendor_sales_analytics(db: Session = Depends(get_db), current_user: User = Depends(require_vendor)):
    return VendorSalesService(db).get_sales_analytics(current_user.id)
