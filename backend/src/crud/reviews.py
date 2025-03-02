from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.db import models
from src.schemas.review import ReviewIn


async def get_by_id(review_id: int, db: AsyncSession) -> models.Review | None:
    return await base.get_one(select(models.Review).filter(models.Review.id == review_id), db)


async def get_by_user(user_id: int, db: AsyncSession) -> list[models.Review]:
    return await base.get_all(select(models.Review).filter(models.Review.user_id == user_id), db)


async def create(product_id: int, user_id: int, review: ReviewIn, db: AsyncSession) -> models.Review | None:
    return await base.create(models.Review(
        product_id=product_id,
        user_id=user_id,
        **review.model_dump(),
    ), db)


async def delete(review_id: int, db: AsyncSession) -> None:
    await base.delete(select(models.Review).filter(models.Review.id == review_id), db)
