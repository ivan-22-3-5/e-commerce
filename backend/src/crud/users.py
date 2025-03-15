from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Creatable
from src.db import models


class UserCRUD(Creatable, Retrievable):
    model = models.User
    key = models.User.id

    @classmethod
    async def get_by_email(cls, email: EmailStr, db: AsyncSession) -> models.User | None:
        return await cls._get_one(models.User.email == email, db)
