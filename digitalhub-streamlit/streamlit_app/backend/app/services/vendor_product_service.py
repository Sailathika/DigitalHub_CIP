import uuid
from typing import List, Optional

from fastapi import HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.vendor_product import VendorProduct
from app.repository.vendor_product_repository import VendorProductRepository
from app.schemas.vendor_product import VendorProductInput, VendorProductOut
from app.utils.file_utils import delete_product_image, save_product_image


def _validation_error_detail(exc: ValidationError) -> str:
    first = exc.errors()[0]
    field = ".".join(str(p) for p in first["loc"])
    return f"{field}: {first['msg']}"


class VendorProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = VendorProductRepository(db)

    def _to_out(self, product: VendorProduct) -> VendorProductOut:
        image_url = f"/static/{product.image_path}" if product.image_path else None
        return VendorProductOut(
            id=product.id,
            vendor_id=product.vendor_id,
            name=product.name,
            category=product.category,
            description=product.description,
            price=product.price,
            stock=product.stock,
            sku=product.sku,
            brand=product.brand,
            image_url=image_url,
            status=product.status.value if hasattr(product.status, "value") else product.status,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    def list_products(self, vendor_id: uuid.UUID, search: Optional[str], category: Optional[str]):
        products = self.repo.list_by_vendor(vendor_id, search=search, category=category)
        categories = self.repo.distinct_categories(vendor_id)
        return [self._to_out(p) for p in products], categories

    def get_product(self, vendor_id: uuid.UUID, product_id: uuid.UUID) -> VendorProductOut:
        product = self.repo.get_for_vendor(product_id, vendor_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return self._to_out(product)

    def _validate(self, raw: dict) -> VendorProductInput:
        try:
            return VendorProductInput(**raw)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=_validation_error_detail(exc)
            ) from exc

    def create_product(
        self,
        vendor_id: uuid.UUID,
        raw: dict,
        image: Optional[UploadFile] = None,
    ) -> VendorProductOut:
        data = self._validate(raw)
        image_path = save_product_image(image) if image and image.filename else None

        product = self.repo.create(
            vendor_id=vendor_id,
            name=data.name,
            category=data.category,
            description=data.description,
            price=data.price,
            stock=data.stock,
            sku=data.sku,
            brand=data.brand,
            status=data.status,
            image_path=image_path,
        )
        return self._to_out(product)

    def update_product(
        self,
        vendor_id: uuid.UUID,
        product_id: uuid.UUID,
        raw: dict,
        image: Optional[UploadFile] = None,
    ) -> VendorProductOut:
        product = self.repo.get_for_vendor(product_id, vendor_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        data = self._validate(raw)
        updates = {
            "name": data.name,
            "category": data.category,
            "description": data.description,
            "price": data.price,
            "stock": data.stock,
            "sku": data.sku,
            "brand": data.brand,
            "status": data.status,
        }

        if image and image.filename:
            old_image_path = product.image_path
            updates["image_path"] = save_product_image(image)
            delete_product_image(old_image_path)

        product = self.repo.update(product, **updates)
        return self._to_out(product)

    def delete_product(self, vendor_id: uuid.UUID, product_id: uuid.UUID) -> None:
        product = self.repo.get_for_vendor(product_id, vendor_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        delete_product_image(product.image_path)
        self.repo.delete(product)

    def list_all_products_admin(self) -> List[VendorProductOut]:
        return [self._to_out(p) for p in self.repo.list_all()]

    def get_inventory(self, vendor_id: uuid.UUID, low_stock_threshold: int = 15):
        products = self.repo.list_by_vendor(vendor_id)
        out = [self._to_out(p) for p in products]

        in_stock = sum(1 for p in products if p.stock > low_stock_threshold)
        low_stock = sum(1 for p in products if 0 < p.stock <= low_stock_threshold)
        out_of_stock = sum(1 for p in products if p.stock <= 0)
        total_value = sum((p.price or 0) * (p.stock or 0) for p in products)

        return {
            "total_products": len(products),
            "in_stock": in_stock,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "total_inventory_value": round(total_value, 2),
            "low_stock_threshold": low_stock_threshold,
            "products": sorted(out, key=lambda p: p.stock),
        }
