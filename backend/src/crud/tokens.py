from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import Retrievable, Deletable, Creatable
from src.db import models


class TokenCRUD(Creatable, Retrievable, Deletable):
    model = models.TokenBase
    key = models.TokenBase.user_id

    @classmethod
    async def upsert(cls, token: models.TokenBase, db: AsyncSession):
        if existing_token := await cls.get(token.user_id, db, on_not_found='return-none'):
            existing_token.token = token.token
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
