from src.crud.base import Retrievable, Deletable, Creatable
from src.db import models


class ReviewCRUD(Creatable, Retrievable, Deletable):
    model = models.Review
    key = models.Review.id

    async def get_by_user(self, user_id: int) -> list[models.Review]:
        return await self._get_all(models.Review.user_id == user_id)

    async def get_by_product(self, product_id: int) -> list[models.Review]:
        return await self._get_all(models.Review.product_id == product_id)
