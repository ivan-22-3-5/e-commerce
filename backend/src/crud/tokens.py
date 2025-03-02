from typing import Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import base
from src.db import models


class TokenCrud:
    def __init__(self, model: Type[models.TokenBase]):
        self.model = model

    async def get_by_user_id(self, user_id: int, db: AsyncSession) -> models.TokenBase | None:
        return await base.get_one(select(self.model).filter(self.model.user_id == user_id), db)

    async def add(self, user_id: int, token: str, db: AsyncSession):
        await base.create(self.model(user_id=user_id,
                                     token=token), db)

    async def update(self, user_id: int, new_token: str, db: AsyncSession):
        await base.update_property(select(self.model).filter(self.model.user_id == user_id),
                                   'token', new_token, db)

    async def delete(self, user_id: int, db: AsyncSession):
        await base.delete(select(self.model).filter(self.model.user_id == user_id), db)


confirmation_tokens = TokenCrud(models.ConfirmationToken)
recovery_tokens = TokenCrud(models.RecoveryToken)
refresh_tokens = TokenCrud(models.RefreshToken)
