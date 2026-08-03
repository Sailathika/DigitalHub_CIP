import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.prediction import CLVPredictResponse, CLVTrainResponse
from app.services.clv_service import CLVService

router = APIRouter(prefix="/clv", tags=["Customer Lifetime Value"])


@router.post("/{dataset_id}/train", response_model=CLVTrainResponse)
def train_clv(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return CLVService(db).train(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{dataset_id}/predict", response_model=CLVPredictResponse)
def predict_clv(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return CLVService(db).predict(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
