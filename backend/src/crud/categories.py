from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Deletable
from src.db import models


class CategoryCRUD(Retrievable, Deletable):
    model = models.Category
    key = models.Category.name

    @classmethod
    async def add_product(cls, category_name: str, product: models.Product, db: AsyncSession):
        category = await cls.get_one(category_name, db)
        if category:
            category.products.append(product)
