import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin, require_vendor
from app.database.session import get_db
from app.models.user import User
from app.schemas.vendor_product import VendorInventoryResponse, VendorProductListResponse, VendorProductOut
from app.services.vendor_product_service import VendorProductService

router = APIRouter(prefix="/vendor/products", tags=["Vendor Products"])


@router.get("/inventory", response_model=VendorInventoryResponse)
def get_inventory(db: Session = Depends(get_db), current_user: User = Depends(require_vendor)):
    return VendorProductService(db).get_inventory(current_user.id)


@router.get("/", response_model=VendorProductListResponse)
def list_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vendor),
):
    products, categories = VendorProductService(db).list_products(current_user.id, search, category)
    return VendorProductListResponse(products=products, categories=categories)


@router.post("/", response_model=VendorProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    name: str = Form(...),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    sku: str = Form(...),
    brand: Optional[str] = Form(None),
    product_status: str = Form("active", alias="status"),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vendor),
):
    raw = {
        "name": name,
        "category": category,
        "description": description,
        "price": price,
        "stock": stock,
        "sku": sku,
        "brand": brand,
        "status": product_status,
    }
    return VendorProductService(db).create_product(current_user.id, raw, image)


@router.get("/admin/all", response_model=list[VendorProductOut])
def list_all_products_admin(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return VendorProductService(db).list_all_products_admin()


@router.get("/{product_id}", response_model=VendorProductOut)
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_vendor)):
    return VendorProductService(db).get_product(current_user.id, product_id)


@router.put("/{product_id}", response_model=VendorProductOut)
def update_product(
    product_id: uuid.UUID,
    name: str = Form(...),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    sku: str = Form(...),
    brand: Optional[str] = Form(None),
    product_status: str = Form("active", alias="status"),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vendor),
):
    raw = {
        "name": name,
        "category": category,
        "description": description,
        "price": price,
        "stock": stock,
        "sku": sku,
        "brand": brand,
        "status": product_status,
    }
    return VendorProductService(db).update_product(current_user.id, product_id, raw, image)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(require_vendor)):
    VendorProductService(db).delete_product(current_user.id, product_id)
    return None
