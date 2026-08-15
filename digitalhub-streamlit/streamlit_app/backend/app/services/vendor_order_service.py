import uuid
from typing import Optional

from sqlalchemy.orm import Session, joinedload
from app.models.customer import Customer
from app.models.order import Order,OrderStatus
from app.models.product import Product
from app.schemas.vendor_order import (
    VendorOrderCustomer,
    VendorOrderListResponse,
    VendorOrderOut,
    VendorOrderProduct,
)


class VendorOrderService:

    def __init__(self, db: Session):
        self.db = db

    def list_orders(
        self,
        vendor_id: uuid.UUID,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> VendorOrderListResponse:

        query = (
            self.db.query(Order)
            .join(Product, Order.product_id == Product.id)
            .options(
                joinedload(Order.customer),
                joinedload(Order.product),
            )
            .filter(
                Product.vendor_id == vendor_id
            )
        )

        # -----------------------------
        # Status filter
        # -----------------------------
        if status and status.lower() != "all":
            query = query.filter(
                Order.status == status.capitalize()
            )
        # -----------------------------
        # Search
        # -----------------------------
        if search:
            search_text = f"%{search.strip()}%"

            query = query.filter(
                (Order.order_ref.ilike(search_text))
                |
                (
                    Order.customer.has(
                        Customer.name.ilike(search_text)
                    )
                )
                |
                (
                    Order.product.has(
                        Product.name.ilike(search_text)
                    )
                )
            )

        orders = (
            query
            .order_by(Order.order_date.desc())
            .all()
        )

        result = []

        for order in orders:

            customer = None

            if order.customer:
                customer = VendorOrderCustomer(
                    id=order.customer.id,
                    name=order.customer.name,
                    email=order.customer.email,
                )

            product = None

            if order.product:
                product = VendorOrderProduct(
                    id=order.product.id,
                    name=order.product.name,
                    category=order.product.category,
                    product_ref=order.product.product_ref,
                )

            result.append(
                VendorOrderOut(
                    id=order.id,
                    order_ref=order.order_ref,
                    order_date=order.order_date,
                    quantity=order.quantity,
                    amount=order.amount,
                    status=order.status,
                    customer=customer,
                    product=product,
                )
            )

        return VendorOrderListResponse(
            orders=result,
            total=len(result),
        )

    def get_order(
        self,
        vendor_id: uuid.UUID,
        order_id: uuid.UUID,
    ) -> VendorOrderOut:

        order = (
            self.db.query(Order)
            .join(Product, Order.product_id == Product.id)
            .options(
                joinedload(Order.customer),
                joinedload(Order.product),
            )
            .filter(
                Order.id == order_id,
                Product.vendor_id == vendor_id,
            )
            .first()
        )

        if not order:
            raise ValueError("Order not found")

        customer = None

        if order.customer:
            customer = VendorOrderCustomer(
                id=order.customer.id,
                name=order.customer.name,
                email=order.customer.email,
            )

        product = None

        if order.product:
            product = VendorOrderProduct(
                id=order.product.id,
                name=order.product.name,
                category=order.product.category,
                product_ref=order.product.product_ref,
            )

        return VendorOrderOut(
            id=order.id,
            order_ref=order.order_ref,
            order_date=order.order_date,
            quantity=order.quantity,
            amount=order.amount,
            status=order.status,
            customer=customer,
            product=product,
        )