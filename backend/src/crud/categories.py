from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.db import models
from src.schemas.category import CategoryIn


async def get_by_name(category_name: str, db: AsyncSession) -> models.Category | None:
    return await base.get_one(select(models.Category).
                              filter(models.Category.name == category_name), db)


async def create(category: CategoryIn, db: AsyncSession) -> models.Category | None:
    return await base.create(models.Category(
        **category.model_dump()
    ), db)


async def add_product(category_name: str, product: models.Product, db: AsyncSession):
    category = await get_by_name(category_name, db)
    if category:
        category.products.append(product)
        await db.commit()
        await db.refresh(category)


async def delete(category_name: str, db: AsyncSession):
    await base.delete(select(models.Category).filter(models.Category.name == category_name), db)
