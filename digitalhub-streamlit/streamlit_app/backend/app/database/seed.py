import os

from app.auth.security import hash_password
from app.database.session import SessionLocal
from app.models.user import User, UserRole
from app.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@digitalhub.io")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "ChangeMe123!")


def seed_default_admin() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == DEFAULT_ADMIN_EMAIL).first()
        if existing:
            return
        admin = User(
            email=DEFAULT_ADMIN_EMAIL,
            hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
            full_name="DigitalHub Admin",
            role=UserRole.ADMIN,
        )
        db.add(admin)
        db.commit()
        logger.info("Seeded default admin account: %s", DEFAULT_ADMIN_EMAIL)
    finally:
        db.close()
