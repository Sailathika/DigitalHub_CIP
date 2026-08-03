import uuid
from typing import List

from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.repository.base import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    def __init__(self, db: Session):
        super().__init__(db, Dataset)

    def list_recent(self, limit: int = 50) -> List[Dataset]:
        return (
            self.db.query(Dataset)
            .order_by(Dataset.uploaded_at.desc())
            .limit(limit)
            .all()
        )
