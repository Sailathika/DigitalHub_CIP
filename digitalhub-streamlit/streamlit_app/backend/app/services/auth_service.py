from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.jwt_handler import create_access_token
from app.auth.security import hash_password, verify_password
from app.config import settings
from app.models.user import User, UserRole
from app.repository.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, VendorRegisterRequest
from app.schemas.settings import ChangePasswordRequest, UpdateProfileRequest


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register_vendor(self, payload: VendorRegisterRequest) -> TokenResponse:
        if self.users.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")

        user = self.users.create(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.owner_name,
            role=UserRole.VENDOR,
            business_name=payload.business_name,
            phone=payload.phone,
            address=payload.address,
        )
        return self._issue_token(user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        if user.role.value != payload.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This account is registered as '{user.role.value}', not '{payload.role}'",
            )
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

        return self._issue_token(user)

    def update_profile(self, user: User, payload: UpdateProfileRequest) -> User:
        updates = {"full_name": payload.full_name}
        if payload.phone is not None:
            updates["phone"] = payload.phone
        if payload.address is not None:
            updates["address"] = payload.address
        if payload.business_name is not None and user.role == UserRole.VENDOR:
            updates["business_name"] = payload.business_name
        return self.users.update(user, **updates)

    def change_password(self, user: User, payload: ChangePasswordRequest) -> None:
        if not verify_password(payload.current_password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
        self.users.update(user, hashed_password=hash_password(payload.new_password))

    def _issue_token(self, user: User) -> TokenResponse:
        token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
        return TokenResponse(
            access_token=token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user,
        )
