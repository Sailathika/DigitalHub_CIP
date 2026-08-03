import uuid
from typing import List

from pydantic import BaseModel


class RecommendedProduct(BaseModel):
    product_id: uuid.UUID
    product_ref: str
    name: str
    category: str
    score: float


class FrequentlyBoughtTogetherResponse(BaseModel):
    dataset_id: uuid.UUID
    product_id: uuid.UUID
    recommendations: List[RecommendedProduct]


class SimilarProductsResponse(BaseModel):
    dataset_id: uuid.UUID
    product_id: uuid.UUID
    recommendations: List[RecommendedProduct]


class PersonalizedRecommendationResponse(BaseModel):
    dataset_id: uuid.UUID
    customer_id: uuid.UUID
    recommendations: List[RecommendedProduct]
