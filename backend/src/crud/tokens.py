from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Deletable, Updatable, Creatable, AbstractCRUD
from src.db import models
from src.db.models import TokenBase


class TokenCRUD(AbstractCRUD, Creatable, Retrievable, Deletable, Updatable):
    @classmethod
    async def upsert(cls, token: TokenBase, db: AsyncSession):
        if await cls.get(token.user_id, db=db):
            await cls.update(token.user_id, token, db=db)
        else:
            await cls.create(token, db=db)


class ConfirmationTokenCRUD(TokenCRUD):
    model = models.ConfirmationToken
    key = models.ConfirmationToken.user_id


class RecoveryTokenCRUD(TokenCRUD):
    model = models.RecoveryToken
    key = models.RecoveryToken.user_id


class RefreshTokenCRUD(TokenCRUD):
    model = models.RefreshToken
    key = models.RefreshToken.user_id
