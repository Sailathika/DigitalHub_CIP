import uuid
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.repository.vendor_product_repository import VendorProductRepository
from app.services.vendor_sales_service import VendorSalesService

PRIMARY = colors.HexColor("#6366F1")
DARK = colors.HexColor("#1E293B")
MUTED = colors.HexColor("#64748B")


def _table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
    )


class VendorReportService:
    def __init__(self, db: Session):
        self.db = db
        self.products = VendorProductRepository(db)
        self.sales = VendorSalesService(db)

    def _pdf_path(self, vendor_id: uuid.UUID) -> Path:
        return settings.REPORTS_DIR / f"vendor_{vendor_id}.pdf"

    def generate_pdf(self, vendor: User) -> Path:
        analytics = self.sales.get_sales_analytics(vendor.id)
        catalog = self.products.list_by_vendor(vendor.id)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="RTitle", fontSize=20, textColor=DARK, spaceAfter=4))
        styles.add(ParagraphStyle(name="RSubtitle", fontSize=10, textColor=MUTED, spaceAfter=18))
        styles.add(ParagraphStyle(name="RHeading", fontSize=13, textColor=PRIMARY, spaceBefore=14, spaceAfter=6))
        styles.add(ParagraphStyle(name="RBody", fontSize=9.5, textColor=DARK, leading=14))

        output_path = self._pdf_path(vendor.id)
        doc = SimpleDocTemplate(
            str(output_path), pagesize=A4,
            leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
        )
        story = [
            Paragraph(f"{vendor.business_name or vendor.full_name} — Performance Report", styles["RTitle"]),
            Paragraph(f"Generated for {vendor.full_name} ({vendor.email})", styles["RSubtitle"]),
            Paragraph("Summary", styles["RHeading"]),
            Table(
                [
                    ["Metric", "Value"],
                    ["Total Revenue", f"Rs. {analytics['total_revenue']:,.0f}"],
                    ["Total Orders", str(analytics["total_orders"])],
                    ["Average Order Value", f"Rs. {analytics['average_order_value']:,.0f}"],
                    ["Products Listed", str(len(catalog))],
                ],
                hAlign="LEFT",
            ),
        ]
        story[-1].setStyle(_table_style())
        story.append(Spacer(1, 12))

        if analytics["sales_by_category"]:
            story.append(Paragraph("Revenue by Category", styles["RHeading"]))
            rows = [["Category", "Revenue"]] + [
                [c["category"], f"Rs. {c['revenue']:,.0f}"] for c in analytics["sales_by_category"]
            ]
            t = Table(rows, hAlign="LEFT")
            t.setStyle(_table_style())
            story.append(t)
            story.append(Spacer(1, 12))

        if analytics["top_products"]:
            story.append(Paragraph("Top Products", styles["RHeading"]))
            rows = [["Product", "Units Sold", "Revenue"]] + [
                [p["name"], str(p["unitsSold"]), f"Rs. {p['revenue']:,.0f}"] for p in analytics["top_products"]
            ]
            t = Table(rows, hAlign="LEFT")
            t.setStyle(_table_style())
            story.append(t)
            story.append(Spacer(1, 12))

        story.append(Paragraph("Product Catalog", styles["RHeading"]))
        rows = [["SKU", "Product", "Category", "Price", "Stock", "Status"]] + [
            [p.sku, p.name, p.category or "—", f"Rs. {p.price:,.0f}", str(p.stock), p.status.value if hasattr(p.status, "value") else p.status]
            for p in catalog
        ]
        t = Table(rows, hAlign="LEFT", repeatRows=1)
        t.setStyle(_table_style())
        story.append(t)

        doc.build(story)
        return output_path

    def export_products_csv(self, vendor_id: uuid.UUID) -> Path:
        catalog = self.products.list_by_vendor(vendor_id)
        rows = [
            {
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "brand": p.brand,
                "price": p.price,
                "stock": p.stock,
                "status": p.status.value if hasattr(p.status, "value") else p.status,
                "created_at": p.created_at,
            }
            for p in catalog
        ]
        df = pd.DataFrame(rows)
        output_path = settings.REPORTS_DIR / f"vendor_products_{vendor_id}.csv"
        df.to_csv(output_path, index=False)
        return output_path
