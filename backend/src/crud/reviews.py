from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Deletable
from src.db import models


class ReviewsCrud(Retrievable, Deletable):
    model = models.Review
    key = models.Review.id

    @classmethod
    async def get_by_user(cls, user_id: int, db: AsyncSession) -> list[models.Review]:
        return await cls._get_all(models.Review.user_id == user_id, db)
