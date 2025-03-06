from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.base import ObjUpdate


class _CRUDBase:
    model = None
    key = None

    @classmethod
    async def _get_one(cls, criteria, db: AsyncSession):
        result = await db.execute(select(cls.model).filter(criteria))
        return result.scalars().first()

    @classmethod
    async def _get_all(cls, criteria, db: AsyncSession):
        result = await db.execute(select(cls.model).filter(criteria))
        return result.scalars().all()


class Creatable(_CRUDBase):
    @classmethod
    async def create(cls, obj, db: AsyncSession):
        try:
            db.add(obj)
            await db.flush()
            return obj
        except IntegrityError as e:
            print(e)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.model is None:
            raise TypeError(f"Class {cls.__name__} must define 'model' class attribute.")


class Retrievable(_CRUDBase):
    @classmethod
    async def get(cls, key, db: AsyncSession):
        return await cls._get_one(cls.key == key, db)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.model is None or cls.key is None:
            raise TypeError(f"Class {cls.__name__} must define 'model' and 'key' class attributes.")


class Updatable(_CRUDBase):
    @classmethod
    async def update(cls, key, obj_update: ObjUpdate, db: AsyncSession):
        obj_to_update = await cls._get_one(cls.key == key, db)
        if obj_to_update:
            for k, v in obj_update.model_dump(exclude_none=True).items():
                setattr(obj_to_update, k, v)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.model is None or cls.key is None:
            raise TypeError(f"Class {cls.__name__} must define 'model' and 'key' class attributes.")


class Deletable(_CRUDBase):
    @classmethod
    async def delete(cls, key, db: AsyncSession):
        obj_to_delete = await cls._get_one(cls.key == key, db)
        if obj_to_delete:
            await db.delete(obj_to_delete)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.model is None or cls.key is None:
            raise TypeError(f"Class {cls.__name__} must define 'model' and 'key' class attributes.")
