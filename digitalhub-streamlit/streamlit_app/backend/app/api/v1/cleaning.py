import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.dataset import CleaningResponse
from app.services.cleaning_service import CleaningService

router = APIRouter(prefix="/datasets", tags=["Data Cleaning"])


@router.post("/{dataset_id}/clean", response_model=CleaningResponse)
def clean_dataset(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CleaningService(db).clean(dataset_id)
