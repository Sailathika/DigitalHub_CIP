import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.customer import CustomerAnalyticsResponse, CustomerOverviewResponse, SalesAnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Customer Analytics"])


@router.get("/{dataset_id}/customer-overview", response_model=CustomerOverviewResponse)
def customer_overview(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AnalyticsService(db).customer_overview(dataset_id)


@router.get("/{dataset_id}/customers", response_model=CustomerAnalyticsResponse)
def customer_analytics(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AnalyticsService(db).customer_analytics(dataset_id)


@router.get("/{dataset_id}/sales", response_model=SalesAnalyticsResponse)
def sales_analytics(dataset_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AnalyticsService(db).sales_analytics(dataset_id)
