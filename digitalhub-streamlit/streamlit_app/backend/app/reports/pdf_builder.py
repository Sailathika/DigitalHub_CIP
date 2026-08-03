"""
Enterprise PDF report builder.

Pure ReportLab (Platypus for layout/tables, reportlab.graphics for charts) —
no external charting dependency, so the report generation path only relies
on the stack specified for this project.
"""
from pathlib import Path
from typing import Dict, List

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PRIMARY = colors.HexColor("#6366F1")
SUCCESS = colors.HexColor("#22C55E")
DANGER = colors.HexColor("#EF4444")
MUTED = colors.HexColor("#64748B")
DARK = colors.HexColor("#1E293B")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", fontSize=22, leading=26, textColor=DARK, spaceAfter=6))
    styles.add(ParagraphStyle(name="ReportSubtitle", fontSize=11, textColor=MUTED, spaceAfter=20))
    styles.add(ParagraphStyle(name="SectionHeading", fontSize=15, textColor=PRIMARY, spaceBefore=16, spaceAfter=8))
    styles.add(ParagraphStyle(name="Body", fontSize=9.5, textColor=DARK, leading=14))
    return styles


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
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]
    )


def _bar_chart(data: List[float], categories: List[str], title: str) -> Drawing:
    drawing = Drawing(420, 180)
    chart = VerticalBarChart()
    chart.x, chart.y, chart.width, chart.height = 30, 20, 370, 140
    chart.data = [data]
    chart.categoryAxis.categoryNames = categories
    chart.categoryAxis.labels.fontSize = 7
    chart.categoryAxis.labels.angle = 0
    chart.valueAxis.valueMin = 0
    chart.bars[0].fillColor = PRIMARY
    chart.barWidth = 8
    drawing.add(chart)
    return drawing


def _line_chart(data: List[float], categories: List[str]) -> Drawing:
    drawing = Drawing(420, 180)
    chart = HorizontalLineChart()
    chart.x, chart.y, chart.width, chart.height = 30, 20, 370, 140
    chart.data = [data]
    chart.categoryAxis.categoryNames = categories
    chart.categoryAxis.labels.fontSize = 7
    chart.lines[0].strokeColor = PRIMARY
    chart.lines[0].strokeWidth = 2
    drawing.add(chart)
    return drawing


def _table_from_rows(headers: List[str], rows: List[List[str]]) -> Table:
    table = Table([headers] + rows, hAlign="LEFT", repeatRows=1)
    table.setStyle(_table_style())
    return table


def build_report(output_path: Path, dataset_name: str, sections: Dict) -> Path:
    """
    `sections` is a dict assembled by ReportService with the following keys
    (all optional except `dataset_summary`):
        executive_summary: str
        dataset_summary: dict
        cleaning_summary: dict
        eda_summary: dict
        customer_analytics: dict
        segmentation: dict
        clv: dict
        churn: dict
        recommendations: dict
    """
    styles = _styles()
    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
    )
    story = []

    # --- Cover / Executive Summary ---
    story.append(Paragraph("DigitalHub Analytics Report", styles["ReportTitle"]))
    story.append(Paragraph(f"Dataset: {dataset_name}", styles["ReportSubtitle"]))
    story.append(Paragraph("Executive Summary", styles["SectionHeading"]))
    story.append(Paragraph(sections.get("executive_summary", ""), styles["Body"]))
    story.append(Spacer(1, 12))

    # --- Dataset Summary ---
    ds = sections.get("dataset_summary", {})
    story.append(Paragraph("Dataset Summary", styles["SectionHeading"]))
    story.append(
        _table_from_rows(
            ["Metric", "Value"],
            [
                ["Rows", str(ds.get("row_count", "—"))],
                ["Columns", str(ds.get("column_count", "—"))],
                ["File Type", str(ds.get("file_type", "—")).upper()],
                ["Status", str(ds.get("status", "—")).title()],
            ],
        )
    )
    story.append(Spacer(1, 12))

    # --- Cleaning Summary ---
    cs = sections.get("cleaning_summary")
    if cs:
        story.append(Paragraph("Data Cleaning Summary", styles["SectionHeading"]))
        story.append(Paragraph(f"{cs.get('rows_before', 0)} rows in → {cs.get('rows_after', 0)} rows out.", styles["Body"]))
        rows = [[i["issue"], str(i["affected_rows"]), i["severity"].title()] for i in cs.get("issues", [])]
        if rows:
            story.append(Spacer(1, 6))
            story.append(_table_from_rows(["Issue", "Affected Rows", "Severity"], rows))
        story.append(Spacer(1, 12))

    # --- EDA Summary ---
    eda = sections.get("eda_summary")
    if eda:
        story.append(Paragraph("Exploratory Data Analysis", styles["SectionHeading"]))
        story.append(
            _table_from_rows(
                ["Metric", "Value"],
                [
                    ["Total Revenue", f"₹{eda.get('total_revenue', 0):,.0f}"],
                    ["Total Orders", str(eda.get("total_orders", 0))],
                    ["Total Customers", str(eda.get("total_customers", 0))],
                    ["Total Products", str(eda.get("total_products", 0))],
                    ["Average Order Value", f"₹{eda.get('average_order_value', 0):,.0f}"],
                ],
            )
        )
        story.append(Spacer(1, 12))

    # --- Customer Analytics + chart ---
    ca = sections.get("customer_analytics")
    if ca:
        story.append(PageBreak())
        story.append(Paragraph("Customer Analytics", styles["SectionHeading"]))
        story.append(
            _table_from_rows(
                ["Metric", "Value"],
                [
                    ["Total Customers", str(ca.get("total_customers", 0))],
                    ["Returning Customers", str(ca.get("returning_customers", 0))],
                    ["Active Customers", str(ca.get("active_customers", 0))],
                    ["Average Order Value", f"₹{ca.get('average_order_value', 0):,.0f}"],
                ],
            )
        )
        trend = ca.get("sales_trend", [])
        if trend:
            story.append(Spacer(1, 10))
            story.append(_line_chart([t["revenue"] for t in trend], [t["month"] for t in trend]))
        story.append(Spacer(1, 12))

    # --- Segmentation ---
    seg = sections.get("segmentation")
    if seg:
        story.append(Paragraph("Customer Segmentation (RFM)", styles["SectionHeading"]))
        distribution = seg.get("distribution", [])
        if distribution:
            story.append(
                _bar_chart(
                    [d["customer_count"] for d in distribution],
                    [d["segment_label"] for d in distribution],
                    "Segment Distribution",
                )
            )
            story.append(Spacer(1, 8))
            story.append(
                _table_from_rows(
                    ["Segment", "Customers", "Total Monetary Value"],
                    [[d["segment_label"], str(d["customer_count"]), f"₹{d['total_monetary']:,.0f}"] for d in distribution],
                )
            )
        story.append(Spacer(1, 12))

    # --- CLV ---
    clv = sections.get("clv")
    if clv:
        story.append(PageBreak())
        story.append(Paragraph("Customer Lifetime Value Prediction", styles["SectionHeading"]))
        story.append(
            Paragraph(
                f"Model: {clv.get('model_version', '—')} · R² = {clv.get('r2_score', 0):.3f} · "
                f"MAE = ₹{clv.get('mae', 0):,.0f}",
                styles["Body"],
            )
        )
        top = clv.get("top_predictions", [])[:10]
        if top:
            story.append(Spacer(1, 8))
            story.append(
                _table_from_rows(
                    ["Customer", "Predicted CLV"],
                    [[p["name"], f"₹{p['predicted_clv']:,.0f}"] for p in top],
                )
            )
        story.append(Spacer(1, 12))

    # --- Churn ---
    churn = sections.get("churn")
    if churn:
        story.append(Paragraph("Customer Churn Prediction", styles["SectionHeading"]))
        story.append(
            Paragraph(
                f"Model: {churn.get('model_version', '—')} · Accuracy = {churn.get('accuracy', 0):.1%} · "
                f"F1 = {churn.get('f1_score', 0):.3f}",
                styles["Body"],
            )
        )
        importance = churn.get("feature_importance", {})
        if importance:
            story.append(Spacer(1, 8))
            story.append(_bar_chart(list(importance.values()), list(importance.keys()), "Feature Importance"))
        high_risk = [p for p in churn.get("predictions", []) if p["risk_level"] == "High"][:10]
        if high_risk:
            story.append(Spacer(1, 8))
            story.append(
                _table_from_rows(
                    ["Customer", "Churn Probability", "Risk"],
                    [[p["name"], f"{p['churn_probability']:.1%}", p["risk_level"]] for p in high_risk],
                )
            )
        story.append(Spacer(1, 12))

    # --- Recommendations ---
    recs = sections.get("recommendations")
    if recs:
        story.append(Paragraph("Product Recommendations", styles["SectionHeading"]))
        rows = [[r["name"], r["category"], f"{r['score']:.2f}"] for r in recs.get("top_recommended", [])[:10]]
        if rows:
            story.append(_table_from_rows(["Product", "Category", "Score"], rows))
        story.append(Spacer(1, 12))

    doc.build(story)
    return output_path
