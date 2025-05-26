from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.config import rules
from src.schemas.user import UserOut


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=0, le=5, description="Оцінка продукту від 0 до 5")
    content: str = Field(
        ..., max_length=rules.MAX_REVIEW_CONTENT_LENGTH, description="Текст відгуку"
    )


class ReviewIn(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(
        None, ge=0, le=5, description="Нова оцінка продукту від 0 до 5"
    )
    content: Optional[str] = Field(
        None,
        max_length=rules.MAX_REVIEW_CONTENT_LENGTH,
        description="Новий текст відгуку",
    )


class ReviewOut(ReviewBase):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True
