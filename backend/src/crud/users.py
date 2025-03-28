from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Creatable
from src.db import models


class UserCRUD(Creatable, Retrievable):
    model = models.User
    key = models.User.id

    @classmethod
    async def get_by_email(cls, email: str, db: AsyncSession) -> models.User | None:
        return await cls._get_one(models.User.email == email, db)

    @classmethod
    async def get_by_idp_id(cls, idp_id: str, db: AsyncSession) -> models.User | None:
        return await cls._get_one(models.User.identity_provider_id == idp_id, db)
