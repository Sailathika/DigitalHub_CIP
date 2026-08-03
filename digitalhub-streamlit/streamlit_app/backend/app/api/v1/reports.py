import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.report import (
    ReportGenerateRequest,
    ReportGenerateResponse,
    ReportListResponse,
    ReportOut,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/{dataset_id}/generate", response_model=ReportGenerateResponse, status_code=201)
def generate_report(
    dataset_id: uuid.UUID,
    options: ReportGenerateRequest = ReportGenerateRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = ReportService(db).generate(dataset_id, options, generated_by=current_user.id)
    report_out = ReportOut.model_validate(report)
    return ReportGenerateResponse(report=report_out, download_url=f"/api/v1/reports/{report.id}/download")


@router.get("/", response_model=ReportListResponse)
def list_reports(
    dataset_id: uuid.UUID = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = ReportService(db).list_reports(dataset_id)
    return ReportListResponse(reports=reports)


@router.get("/{report_id}/download")
def download_report(report_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from fastapi import HTTPException, status

    from app.models.report import Report

    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return FileResponse(report.file_path, media_type="application/pdf", filename=f"{report.name}.pdf")


@router.get("/{dataset_id}/export-csv")
def export_customers_csv(
    dataset_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    csv_path = ReportService(db).export_customers_csv(dataset_id)
    return FileResponse(csv_path, media_type="text/csv", filename=csv_path.name)
