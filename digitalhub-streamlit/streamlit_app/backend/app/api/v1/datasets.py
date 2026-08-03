import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.dataset import DatasetListResponse, DatasetOut
from app.services.upload_service import UploadService

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post("/upload", response_model=DatasetOut, status_code=201)
def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = UploadService(db).upload(file, uploaded_by=current_user.id)
    return dataset


@router.get("/", response_model=DatasetListResponse)
def list_datasets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    datasets = UploadService(db).list_history()
    return DatasetListResponse(datasets=datasets)


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.utils.response_utils import get_dataset_or_404

    return get_dataset_or_404(db, dataset_id)
