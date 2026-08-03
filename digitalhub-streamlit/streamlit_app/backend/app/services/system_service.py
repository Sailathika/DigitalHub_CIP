from sqlalchemy.orm import Session

from app.config import settings
from app.models.dataset import Dataset
from app.models.user import User, UserRole
from app.schemas.settings import SystemInfoResponse


class SystemService:
    def __init__(self, db: Session):
        self.db = db

    def get_system_info(self) -> SystemInfoResponse:
        total_users = self.db.query(User).count()
        total_admins = self.db.query(User).filter(User.role == UserRole.ADMIN).count()
        total_vendors = self.db.query(User).filter(User.role == UserRole.VENDOR).count()
        total_datasets = self.db.query(Dataset).count()

        database_engine = "PostgreSQL" if not settings.DATABASE_URL.startswith("sqlite") else "SQLite"

        return SystemInfoResponse(
            app_name=settings.APP_NAME,
            app_version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
            database_engine=database_engine,
            total_users=total_users,
            total_admins=total_admins,
            total_vendors=total_vendors,
            total_datasets=total_datasets,
            mlflow_tracking_uri=settings.MLFLOW_TRACKING_URI,
        )
