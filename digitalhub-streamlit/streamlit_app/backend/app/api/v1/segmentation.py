import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.prediction import RFMResponse
from app.services.segmentation_service import SegmentationService

router = APIRouter(prefix="/segmentation", tags=["Customer Segmentation"])


@router.post("/{dataset_id}/rfm", response_model=RFMResponse)
def compute_rfm(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return SegmentationService(db).compute_rfm_segmentation(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{dataset_id}", response_model=RFMResponse)
def get_segmentation(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return SegmentationService(db).get_segmentation(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
