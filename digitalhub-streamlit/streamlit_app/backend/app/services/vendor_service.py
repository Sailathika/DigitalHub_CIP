import uuid
from typing import List, Optional

import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.models.order import Order
from app.models.product import Product
from app.models.user import User, UserRole, VendorStatus
from app.repository.user_repository import UserRepository
from app.schemas.vendor import (
    RecentActivityItem,
    VendorCommissionUpdateRequest,
    VendorCreateRequest,
    VendorDetailResponse,
    VendorOut,
    VendorStatusUpdateRequest,
    VendorUpdateRequest,
)
from app.utils.response_utils import clean_number

VENDOR_CATEGORIES = [
    "Smartphones",
    "Laptops & Computers",
    "Audio & Headphones",
    "Wearables",
    "Cameras & Drones",
    "Gaming",
    "Home Appliances",
    "Networking",
    "Accessories",
]


class VendorService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def _base_query(self):
        return self.db.query(User).filter(User.role == UserRole.VENDOR)

    def list_vendors(self, search: Optional[str] = None, status_filter: Optional[str] = None,
                      category: Optional[str] = None) -> List[User]:
        query = self._base_query()
        if search:
            like = f"%{search.strip().lower()}%"
            query = query.filter(
                (User.business_name.ilike(like)) | (User.full_name.ilike(like)) | (User.email.ilike(like))
            )
        if status_filter and status_filter != "all":
            query = query.filter(User.vendor_status == VendorStatus(status_filter))
        if category and category != "all":
            query = query.filter(User.category == category)
        return query.order_by(User.created_at.desc()).all()

    def get_vendor(self, vendor_id: uuid.UUID) -> User:
        vendor = self.db.query(User).filter(User.id == vendor_id, User.role == UserRole.VENDOR).first()
        if vendor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
        return vendor

    def create_vendor(self, payload: VendorCreateRequest) -> User:
        if self.users.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")

        vendor = self.users.create(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.owner_name,
            role=UserRole.VENDOR,
            business_name=payload.business_name,
            phone=payload.phone,
            address=payload.address,
            category=payload.category,
            gst_number=payload.gst_number,
            commission_percent=payload.commission_percent,
            vendor_status=VendorStatus.ACTIVE,
        )
        return vendor

    def update_vendor(self, vendor_id: uuid.UUID, payload: VendorUpdateRequest) -> User:
        vendor = self.get_vendor(vendor_id)
        updates = {}
        if payload.business_name is not None:
            updates["business_name"] = payload.business_name
        if payload.owner_name is not None:
            updates["full_name"] = payload.owner_name
        if payload.phone is not None:
            updates["phone"] = payload.phone
        if payload.address is not None:
            updates["address"] = payload.address
        if payload.category is not None:
            updates["category"] = payload.category
        if payload.gst_number is not None:
            updates["gst_number"] = payload.gst_number
        return self.users.update(vendor, **updates)

    def delete_vendor(self, vendor_id: uuid.UUID) -> None:
        vendor = self.get_vendor(vendor_id)
        # Products already loaded under this vendor keep their sales history —
        # only the vendor_id link is cleared (ON DELETE SET NULL).
        self.users.delete(vendor)

    def update_status(self, vendor_id: uuid.UUID, payload: VendorStatusUpdateRequest) -> User:
        vendor = self.get_vendor(vendor_id)
        new_status = VendorStatus(payload.status)
        is_active = new_status != VendorStatus.SUSPENDED
        return self.users.update(vendor, vendor_status=new_status, is_active=is_active)

    def approve_vendor(self, vendor_id: uuid.UUID) -> User:
        vendor = self.get_vendor(vendor_id)
        return self.users.update(vendor, vendor_status=VendorStatus.ACTIVE, is_active=True)

    def suspend_vendor(self, vendor_id: uuid.UUID) -> User:
        vendor = self.get_vendor(vendor_id)
        return self.users.update(vendor, vendor_status=VendorStatus.SUSPENDED, is_active=False)

    def activate_vendor(self, vendor_id: uuid.UUID) -> User:
        vendor = self.get_vendor(vendor_id)
        return self.users.update(vendor, vendor_status=VendorStatus.ACTIVE, is_active=True)

    def update_commission(self, vendor_id: uuid.UUID, payload: VendorCommissionUpdateRequest) -> User:
        vendor = self.get_vendor(vendor_id)
        return self.users.update(vendor, commission_percent=payload.commission_percent)

    def get_vendor_detail(self, vendor_id: uuid.UUID) -> VendorDetailResponse:
        vendor = self.get_vendor(vendor_id)

        products = self.db.query(Product).filter(Product.vendor_id == vendor_id).all()
        product_ids = [p.id for p in products]
        orders = (
            self.db.query(Order).filter(Order.product_id.in_(product_ids)).all() if product_ids else []
        )

        total_revenue = sum(o.amount for o in orders)
        total_orders = len(orders)

        sales_trend = []
        if orders:
            df = pd.DataFrame([{"order_date": o.order_date, "amount": o.amount} for o in orders])
            df["month"] = pd.to_datetime(df["order_date"]).dt.to_period("M")
            grouped = df.groupby("month")["amount"].sum().sort_index().tail(12)
            sales_trend = [{"month": m.strftime("%b"), "revenue": round(float(v), 2)} for m, v in grouped.items()]

        top_products = sorted(
            [
                {
                    "product_ref": p.product_ref,
                    "name": p.name,
                    "unitsSold": p.total_units_sold,
                    "revenue": round(clean_number(p.total_revenue), 2),
                }
                for p in products
            ],
            key=lambda item: item["revenue"],
            reverse=True,
        )[:5]

        recent_orders = sorted(orders, key=lambda o: o.order_date, reverse=True)[:6]
        recent_orders_out = [
            {
                "id": str(o.id),
                "customer": o.customer.name if o.customer else None,
                "amount": round(clean_number(o.amount), 2),
                "date": o.order_date.strftime("%Y-%m-%d") if o.order_date else None,
                "quantity": o.quantity,
            }
            for o in recent_orders
        ]

        recent_activity = [
            RecentActivityItem(label=f"Order for {o.amount:,.0f} recorded", timestamp=o.order_date)
            for o in recent_orders[:5]
            if o.order_date
        ]
        recent_activity.append(RecentActivityItem(label="Vendor account created", timestamp=vendor.created_at))

        return VendorDetailResponse(
            vendor=VendorOut.model_validate(vendor),
            total_products=len(products),
            total_orders=total_orders,
            total_revenue=round(clean_number(total_revenue), 2),
            sales_trend=sales_trend,
            top_products=top_products,
            recent_orders=recent_orders_out,
            recent_activity=sorted(recent_activity, key=lambda a: a.timestamp, reverse=True),
        )
