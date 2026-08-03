import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.dataset import ValidationResponse
from app.services.validation_service import ValidationService

router = APIRouter(prefix="/datasets", tags=["Data Validation"])


@router.post("/{dataset_id}/validate", response_model=ValidationResponse)
def validate_dataset(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ValidationService(db).validate(dataset_id)
