import uuid

from sqlalchemy.orm import Session

from app.models.dataset import DatasetStatus
from app.preprocessing.validators import validate_dataset
from app.repository.dataset_repository import DatasetRepository
from app.schemas.dataset import ValidationCheck, ValidationResponse
from app.utils.file_utils import read_dataset
from app.utils.response_utils import get_dataset_or_404


class ValidationService:
    def __init__(self, db: Session):
        self.db = db
        self.datasets = DatasetRepository(db)

    def validate(self, dataset_id: uuid.UUID) -> ValidationResponse:
        dataset = get_dataset_or_404(self.db, dataset_id)
        df = read_dataset(dataset.file_path, dataset.file_type)

        raw_checks = validate_dataset(df)
        checks = [ValidationCheck(**c) for c in raw_checks]
        passed = sum(1 for c in checks if c.status == "Passed")

        self.datasets.update(dataset, status=DatasetStatus.VALIDATED)

        return ValidationResponse(dataset_id=dataset_id, checks=checks, passed=passed, total=len(checks))
