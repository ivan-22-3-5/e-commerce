from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.db import models


class ProductCrud(base.Updatable, base.Deletable):
    def __init__(self):
        super().__init__(models.Product, models.Product.id)

    async def get_all(self, *, enabled: bool | None = None, db: AsyncSession) -> list[models.Product] | None:
        return await self._get_all(models.Product.enabled == enabled if enabled is not None else True, db)


products = ProductCrud()
