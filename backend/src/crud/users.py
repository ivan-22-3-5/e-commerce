from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.db import models


class UserCrud(base.Retrievable):
    def __init__(self):
        super().__init__(models.User, models.User.id)

    async def get_by_email(self, email: EmailStr, db: AsyncSession) -> models.User | None:
        return await self.get_one(models.User.email == email, db)

    async def update_password(self, user_id: int, new_password: str, db: AsyncSession):
        user = await self.get_one(user_id, db)
        user.password = new_password

    async def confirm_email(self, user_id: int, db: AsyncSession):
        user = await self.get_one(user_id, db)
        user.is_confirmed = True


users = UserCrud()
