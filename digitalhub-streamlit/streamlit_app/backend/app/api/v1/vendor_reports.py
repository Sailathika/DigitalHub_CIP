from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import require_vendor
from app.database.session import get_db
from app.models.user import User
from app.services.vendor_reports_service import VendorReportService

router = APIRouter(prefix="/vendor/reports", tags=["Vendor Reports"])


@router.get("")
def list_vendor_reports(current_user: User = Depends(require_vendor)):
    return {
        "reports": [
            {
                "id": "performance-report",
                "name": "Performance Report",
                "description": "Revenue, top products, and full product catalog for your store.",
                "format": "pdf",
            },
            {
                "id": "product-catalog",
                "name": "Product Catalog Export",
                "description": "All your products with price, stock, and status.",
                "format": "csv",
            },
        ]
    }


@router.get("/performance-report/download")
def download_performance_report(db: Session = Depends(get_db), current_user: User = Depends(require_vendor)):
    path = VendorReportService(db).generate_pdf(current_user)
    return FileResponse(path, media_type="application/pdf", filename="performance-report.pdf")


@router.get("/product-catalog/download")
def download_product_catalog_csv(db: Session = Depends(get_db), current_user: User = Depends(require_vendor)):
    path = VendorReportService(db).export_products_csv(current_user.id)
    return FileResponse(path, media_type="text/csv", filename="product-catalog.csv")
