import uuid
from typing import List, Optional

from fastapi import UploadFile

from app.models.dataset import Dataset, DatasetStatus
from app.repository.dataset_repository import DatasetRepository
from app.utils.file_utils import read_dataset, save_upload_file


class UploadService:
    def __init__(self, db):
        self.db = db
        self.datasets = DatasetRepository(db)

    def upload(self, file: UploadFile, uploaded_by: Optional[uuid.UUID] = None) -> Dataset:
        stored_filename, file_path, file_type = save_upload_file(file)
        df = read_dataset(file_path, file_type)

        dataset = self.datasets.create(
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_type=file_type,
            row_count=int(len(df)),
            column_count=int(len(df.columns)),
            status=DatasetStatus.UPLOADED,
            uploaded_by=uploaded_by,
        )
        return dataset

    def list_history(self) -> List[Dataset]:
        return self.datasets.list_recent()
