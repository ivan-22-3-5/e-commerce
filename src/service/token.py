from typing import Literal

from src.crud import RefreshTokenCRUD, RecoveryTokenCRUD


class TokenService:
    def __init__(self, refresh_token_crud: RefreshTokenCRUD, recovery_token_crud: RecoveryTokenCRUD):
        self.refresh_token_crud = refresh_token_crud
        self.recovery_token_crud = recovery_token_crud

    async def upsert_refresh_token(self, user_id: int, token: str):
        await self.refresh_token_crud.upsert(user_id, token)

    async def upsert_recovery_token(self, user_id: int, token: str):
        await self.recovery_token_crud.upsert(user_id, token)

    async def revoke_refresh_token(self, user_id: int):
        await self.refresh_token_crud.delete(user_id)

    async def revoke_recovery_token(self, user_id: int):
        await self.recovery_token_crud.delete(user_id)

    async def is_recovery_token_valid(self, user_id: int, token: str) -> bool:
        db_token = await self.recovery_token_crud.get(user_id, on_not_found='return-none')

        return db_token and db_token.token == token

    async def is_refresh_token_valid(self, user_id: int, token: str) -> bool:
        db_token = await self.refresh_token_crud.get(user_id, on_not_found='return-none')

        return db_token and db_token.token == token
