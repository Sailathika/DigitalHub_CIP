import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.dataset import ETLRunResponse
from app.services.etl_service import ETLService

router = APIRouter(prefix="/datasets", tags=["ETL Pipeline"])


@router.post("/{dataset_id}/etl", response_model=ETLRunResponse)
def run_etl(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ETLService(db).run(dataset_id)
