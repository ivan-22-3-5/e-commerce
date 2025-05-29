from src.crud.base import Retrievable, Deletable, Creatable
from src.db import models


class TokenCRUD(Creatable, Retrievable, Deletable):
    model = models.TokenBase
    key = models.TokenBase.user_id

    async def upsert(self, user_id: int, token: str):
        if existing_token := await self.get(user_id, on_not_found='return-none'):
            existing_token.token = token
        else:
            await self.create(
                self.__class__.model(user_id=user_id, token=token)
            )


class RecoveryTokenCRUD(TokenCRUD):
    model = models.RecoveryToken
    key = models.RecoveryToken.user_id


class RefreshTokenCRUD(TokenCRUD):
    model = models.RefreshToken
    key = models.RefreshToken.user_id
