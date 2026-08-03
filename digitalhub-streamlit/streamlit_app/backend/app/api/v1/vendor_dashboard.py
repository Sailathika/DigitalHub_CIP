from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_vendor
from app.database.session import get_db
from app.models.user import User
from app.services.vendor_dashboard_service import VendorDashboardService

router = APIRouter(prefix="/vendor/dashboard", tags=["Vendor Dashboard"])


@router.get("/overview")
def get_vendor_dashboard_overview(db: Session = Depends(get_db), current_user: User = Depends(require_vendor)):
    return VendorDashboardService(db).get_overview(current_user.id)
