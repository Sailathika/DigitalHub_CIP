import uuid

from sqlalchemy.orm import Session

from app.models.dataset import DatasetStatus
from app.preprocessing.cleaners import clean_dataset
from app.repository.dataset_repository import DatasetRepository
from app.schemas.dataset import CleaningIssue, CleaningResponse
from app.utils.file_utils import read_dataset, write_cleaned_dataset
from app.utils.response_utils import get_dataset_or_404


class CleaningService:
    def __init__(self, db: Session):
        self.db = db
        self.datasets = DatasetRepository(db)

    def clean(self, dataset_id: uuid.UUID) -> CleaningResponse:
        dataset = get_dataset_or_404(self.db, dataset_id)
        df = read_dataset(dataset.file_path, dataset.file_type)
        rows_before = len(df)

        cleaned_df, raw_issues = clean_dataset(df)
        rows_after = len(cleaned_df)

        cleaned_path = write_cleaned_dataset(cleaned_df, dataset_id)

        self.datasets.update(
            dataset,
            status=DatasetStatus.CLEANED,
            cleaned_file_path=cleaned_path,
            row_count=rows_after,
        )

        issues = [CleaningIssue(**issue) for issue in raw_issues]
        return CleaningResponse(
            dataset_id=dataset_id, issues=issues, rows_before=rows_before, rows_after=rows_after
        )
