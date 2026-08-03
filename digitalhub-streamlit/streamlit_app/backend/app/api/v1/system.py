from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.settings import SystemInfoResponse
from app.services.system_service import SystemService

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/info", response_model=SystemInfoResponse)
def get_system_info(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return SystemService(db).get_system_info()
