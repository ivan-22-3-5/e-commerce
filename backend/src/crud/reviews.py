from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.db import models


class ReviewsCrud(base.Deletable):
    def __init__(self):
        super().__init__(models.Review, models.Review.id)

    async def get_by_user(self, user_id: int, db: AsyncSession) -> list[models.Review]:
        return await self._get_all(models.Review.user_id == user_id, db)


reviews = ReviewsCrud()
