from typing import Any

from sqlalchemy import Executable
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.base import ObjUpdate


async def get_one(query: Executable, db: AsyncSession):
    result = await db.execute(query)
    return result.scalars().first()


async def get_all(query: Executable, db: AsyncSession):
    result = await db.execute(query)
    return result.scalars().all()


async def create(obj_to_create, db: AsyncSession):
    db.add(obj_to_create)
    await db.commit()
    await db.refresh(obj_to_create)
    return obj_to_create


async def update(query: Executable, obj_update: ObjUpdate, db: AsyncSession):
    obj_to_update = await get_one(query, db)
    if obj_to_update:
        for k, v in obj_update.model_dump(exclude_none=True).items():
            setattr(obj_to_update, k, v)
        await db.commit()
        await db.refresh(obj_to_update)
        return obj_to_update


async def delete(query: Executable, db: AsyncSession):
    obj_to_delete = await get_one(query, db)
    if obj_to_delete:
        await db.delete(obj_to_delete)
        await db.commit()


async def update_property(query: Executable, property_name: str, new_value: Any, db: AsyncSession):
    obj_to_update = await get_one(query, db)
    if obj_to_update:
        setattr(obj_to_update, property_name, new_value)
        await db.commit()
