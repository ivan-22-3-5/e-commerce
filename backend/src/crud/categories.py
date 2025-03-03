from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.db import models


class CategoryCrud(base.Deletable):
    def __init__(self):
        super().__init__(models.Category, models.Category.name)

    async def add_product(self, category_name: str, product: models.Product, db: AsyncSession):
        category = await self.get_one(category_name, db)
        if category:
            category.products.append(product)
