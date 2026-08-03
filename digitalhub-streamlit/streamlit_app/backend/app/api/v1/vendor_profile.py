from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_vendor
from app.database.session import get_db
from app.models.user import User
from app.schemas.vendor_profile import VendorProfileOut, VendorProfileUpdateRequest
from app.services.vendor_profile_service import VendorProfileService

router = APIRouter(prefix="/vendor/profile", tags=["Vendor Profile"])


@router.get("", response_model=VendorProfileOut)
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(require_vendor)):
    return VendorProfileService(db).get_profile(current_user)


@router.put("", response_model=VendorProfileOut)
def update_profile(
    payload: VendorProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vendor),
):
    return VendorProfileService(db).update_profile(current_user, payload)
