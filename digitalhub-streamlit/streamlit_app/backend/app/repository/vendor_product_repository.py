import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.vendor_product import VendorProduct
from app.repository.base import BaseRepository


class VendorProductRepository(BaseRepository[VendorProduct]):
    def __init__(self, db: Session):
        super().__init__(db, VendorProduct)

    def list_by_vendor(
        self, vendor_id: uuid.UUID, search: Optional[str] = None, category: Optional[str] = None
    ) -> List[VendorProduct]:
        query = self.db.query(VendorProduct).filter(VendorProduct.vendor_id == vendor_id)
        if search:
            like = f"%{search.strip().lower()}%"
            query = query.filter(
                (VendorProduct.name.ilike(like))
                | (VendorProduct.sku.ilike(like))
                | (VendorProduct.brand.ilike(like))
            )
        if category and category != "all":
            query = query.filter(VendorProduct.category == category)
        return query.order_by(VendorProduct.created_at.desc()).all()

    def get_for_vendor(self, product_id: uuid.UUID, vendor_id: uuid.UUID) -> Optional[VendorProduct]:
        return (
            self.db.query(VendorProduct)
            .filter(VendorProduct.id == product_id, VendorProduct.vendor_id == vendor_id)
            .first()
        )

    def list_all(self) -> List[VendorProduct]:
        return self.db.query(VendorProduct).order_by(VendorProduct.created_at.desc()).all()

    def distinct_categories(self, vendor_id: uuid.UUID) -> List[str]:
        rows = (
            self.db.query(VendorProduct.category)
            .filter(VendorProduct.vendor_id == vendor_id, VendorProduct.category.isnot(None))
            .distinct()
            .all()
        )
        return sorted({row[0] for row in rows if row[0]})
