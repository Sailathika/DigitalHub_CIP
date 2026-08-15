from fastapi import APIRouter
from app.api.v1 import (
    auth,
    churn,
    clv,
    customer_analytics,
    dashboard,
    datasets,
    cleaning,
    etl,
    recommendations,
    reports,
    segmentation,
    system,
    validation,
    vendor_dashboard,
    vendor_products,
    vendor_profile,
    vendor_reports,
    vendor_sales,
    vendor_orders,       # ← ADD THIS
    vendors,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(vendors.router)
api_router.include_router(vendor_products.router)
api_router.include_router(vendor_profile.router)
api_router.include_router(vendor_dashboard.router)
api_router.include_router(vendor_orders.router)
api_router.include_router(vendor_sales.router)
api_router.include_router(vendor_reports.router)
api_router.include_router(datasets.router)
api_router.include_router(validation.router)
api_router.include_router(cleaning.router)
api_router.include_router(etl.router)
api_router.include_router(customer_analytics.router)
api_router.include_router(segmentation.router)
api_router.include_router(clv.router)
api_router.include_router(churn.router)
api_router.include_router(recommendations.router)
api_router.include_router(reports.router)
api_router.include_router(system.router)
