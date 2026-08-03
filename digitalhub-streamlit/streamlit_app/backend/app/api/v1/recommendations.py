import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.recommendation import (
    FrequentlyBoughtTogetherResponse,
    PersonalizedRecommendationResponse,
    SimilarProductsResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Product Recommendations"])


@router.get("/{dataset_id}/frequently-bought-together", response_model=FrequentlyBoughtTogetherResponse)
def frequently_bought_together(
    dataset_id: uuid.UUID,
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return RecommendationService(db).frequently_bought_together(dataset_id, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{dataset_id}/similar-products", response_model=SimilarProductsResponse)
def similar_products(
    dataset_id: uuid.UUID,
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return RecommendationService(db).similar_products(dataset_id, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{dataset_id}/personalized", response_model=PersonalizedRecommendationResponse)
def personalized_recommendations(
    dataset_id: uuid.UUID,
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return RecommendationService(db).personalized(dataset_id, customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
