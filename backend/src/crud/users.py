from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable
from src.db import models


class UserCrud(Retrievable):
    model = models.User
    key = models.User.id

    @classmethod
    async def get_by_email(cls, email: EmailStr, db: AsyncSession) -> models.User | None:
        return await cls.get_one(models.User.email == email, db)

    @classmethod
    async def update_password(cls, user_id: int, new_password: str, db: AsyncSession):
        user = await cls.get_one(user_id, db)
        user.password = new_password

    @classmethod
    async def confirm_email(cls, user_id: int, db: AsyncSession):
        user = await cls.get_one(user_id, db)
        user.is_confirmed = True
