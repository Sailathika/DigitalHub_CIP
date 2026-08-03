import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.prediction import ChurnPredictResponse, ChurnTrainResponse
from app.services.churn_service import ChurnService

router = APIRouter(prefix="/churn", tags=["Customer Churn"])


@router.post("/{dataset_id}/train", response_model=ChurnTrainResponse)
def train_churn(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return ChurnService(db).train(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{dataset_id}/predict", response_model=ChurnPredictResponse)
def predict_churn(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return ChurnService(db).predict(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
