from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Updatable, Deletable, Creatable
from src.db import models


class ProductCRUD(Creatable, Retrievable, Updatable, Deletable):
    model = models.Product
    key = models.Product.id

    @classmethod
    async def get_all(cls, *, enabled: bool | None = None, db: AsyncSession) -> list[models.Product] | None:
        # TODO: rewrite condition
        return await cls._get_all(models.Product.enabled == enabled if enabled is not None else True, db)
