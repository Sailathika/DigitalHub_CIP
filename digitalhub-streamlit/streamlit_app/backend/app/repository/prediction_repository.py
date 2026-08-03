import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.prediction import CLVPrediction, ChurnPrediction
from app.models.segmentation import CustomerSegment
from app.repository.base import BaseRepository


class SegmentationRepository(BaseRepository[CustomerSegment]):
    def __init__(self, db: Session):
        super().__init__(db, CustomerSegment)

    def list_by_dataset(self, dataset_id: uuid.UUID) -> List[CustomerSegment]:
        return self.db.query(CustomerSegment).filter(CustomerSegment.dataset_id == dataset_id).all()

    def get_by_customer(self, customer_id: uuid.UUID) -> Optional[CustomerSegment]:
        return self.db.query(CustomerSegment).filter(CustomerSegment.customer_id == customer_id).first()

    def delete_by_dataset(self, dataset_id: uuid.UUID) -> None:
        self.db.query(CustomerSegment).filter(CustomerSegment.dataset_id == dataset_id).delete()
        self.db.commit()


class CLVRepository(BaseRepository[CLVPrediction]):
    def __init__(self, db: Session):
        super().__init__(db, CLVPrediction)

    def list_by_dataset(self, dataset_id: uuid.UUID) -> List[CLVPrediction]:
        return self.db.query(CLVPrediction).filter(CLVPrediction.dataset_id == dataset_id).all()

    def delete_by_dataset(self, dataset_id: uuid.UUID) -> None:
        self.db.query(CLVPrediction).filter(CLVPrediction.dataset_id == dataset_id).delete()
        self.db.commit()


class ChurnRepository(BaseRepository[ChurnPrediction]):
    def __init__(self, db: Session):
        super().__init__(db, ChurnPrediction)

    def list_by_dataset(self, dataset_id: uuid.UUID) -> List[ChurnPrediction]:
        return self.db.query(ChurnPrediction).filter(ChurnPrediction.dataset_id == dataset_id).all()

    def delete_by_dataset(self, dataset_id: uuid.UUID) -> None:
        self.db.query(ChurnPrediction).filter(ChurnPrediction.dataset_id == dataset_id).delete()
        self.db.commit()
