import uuid
from typing import List

from sqlalchemy.orm import Session, joinedload

from app.models.customer import Customer
from app.models.order import Order
from app.models.product import Product
from app.repository.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: Session):
        super().__init__(db, Customer)

    def list_by_dataset(self, dataset_id: uuid.UUID) -> List[Customer]:
        return self.db.query(Customer).filter(Customer.dataset_id == dataset_id).all()

    def list_by_dataset_with_segment(self, dataset_id: uuid.UUID) -> List[Customer]:
        return (
            self.db.query(Customer)
            .options(joinedload(Customer.segment))
            .filter(Customer.dataset_id == dataset_id)
            .all()
        )

    def delete_by_dataset(self, dataset_id: uuid.UUID) -> None:
        self.db.query(Customer).filter(Customer.dataset_id == dataset_id).delete()
        self.db.commit()


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(db, Order)

    def list_by_dataset(self, dataset_id: uuid.UUID) -> List[Order]:
        return self.db.query(Order).filter(Order.dataset_id == dataset_id).all()

    def list_by_customer(self, customer_id: uuid.UUID) -> List[Order]:
        return self.db.query(Order).filter(Order.customer_id == customer_id).all()

    def delete_by_dataset(self, dataset_id: uuid.UUID) -> None:
        self.db.query(Order).filter(Order.dataset_id == dataset_id).delete()
        self.db.commit()


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(db, Product)

    def list_by_dataset(self, dataset_id: uuid.UUID) -> List[Product]:
        return self.db.query(Product).filter(Product.dataset_id == dataset_id).all()

    def delete_by_dataset(self, dataset_id: uuid.UUID) -> None:
        self.db.query(Product).filter(Product.dataset_id == dataset_id).delete()
        self.db.commit()
