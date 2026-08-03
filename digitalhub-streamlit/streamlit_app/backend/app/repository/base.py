import uuid
from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.database.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing CRUD operations for a SQLAlchemy model.

    Concrete repositories subclass this and add domain-specific queries
    (e.g. `get_by_dataset`), keeping raw ORM/session usage out of the
    service layer.
    """

    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get(self, id_: uuid.UUID) -> Optional[ModelType]:
        return self.db.get(self.model, id_)

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def bulk_create(self, objects: List[ModelType]) -> List[ModelType]:
        self.db.add_all(objects)
        self.db.commit()
        for obj in objects:
            self.db.refresh(obj)
        return objects

    def update(self, obj: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.commit()
