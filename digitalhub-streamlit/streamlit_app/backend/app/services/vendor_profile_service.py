from sqlalchemy.orm import Session

from app.models.user import User
from app.repository.user_repository import UserRepository
from app.schemas.vendor_profile import VendorProfileOut, VendorProfileUpdateRequest


class VendorProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def _to_out(self, user: User) -> VendorProfileOut:
        return VendorProfileOut(
            id=user.id,
            business_name=user.business_name,
            owner_name=user.full_name,
            email=user.email,
            phone=user.phone,
            gst_number=user.gst_number,
            address=user.address,
            city=user.city,
            state=user.state,
        )

    def get_profile(self, user: User) -> VendorProfileOut:
        return self._to_out(user)

    def update_profile(self, user: User, payload: VendorProfileUpdateRequest) -> VendorProfileOut:
        updated = self.users.update(
            user,
            business_name=payload.business_name,
            full_name=payload.owner_name,
            phone=payload.phone,
            gst_number=payload.gst_number,
            address=payload.address,
            city=payload.city,
            state=payload.state,
        )
        return self._to_out(updated)
