from redis.asyncio import Redis

from src.config import rules
from src.crud.users import UserCRUD
from src.custom_exceptions import InvalidConfirmationCodeError, ResourceAlreadyExistsError, EmailNotConfirmedError
from src.db.models import User
from src.schemas.user import UserIn, GoogleUserInfo


class UserService:
    def __init__(self, user_crud: UserCRUD, redis: Redis):
        self.user_crud = user_crud
        self.redis = redis

    async def register_user(self, user_data: UserIn) -> User:
        confirmation_code_from_redis = await self.redis.get(f"confirmation_code:{user_data.email}")

        if confirmation_code_from_redis is None:
            raise InvalidConfirmationCodeError("Confirmation code not found or expired.")
        if int(confirmation_code_from_redis) != user_data.confirmation_code:
            raise InvalidConfirmationCodeError("Invalid confirmation code.")

        await self.redis.delete(f"confirmation_code:{user_data.email}")

        created_user = await self.user_crud.create(User(**user_data.model_dump(exclude={'confirmation_code'})))
        return created_user

    async def register_user_using_google(self, user_info: GoogleUserInfo) -> User:
        if (await self.user_crud.get_by_email(user_info.email)) is not None:
            raise ResourceAlreadyExistsError("User with this email already registered.")

        if not user_info.email_verified:
            raise EmailNotConfirmedError("Cannot register user with unverified Google email.")

        return await self.user_crud.create(User(
            identity_provider_id=user_info.id,
            email=user_info.email,
            password=None,
            name=user_info.name[:rules.MAX_USERNAME_LENGTH]
        ))

    async def get_user_by_identity_provider_id(self, identity_provider_id: str) -> User | None:
        return await self.user_crud.get_by_idp_id(identity_provider_id)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_crud.get(user_id, on_not_found='return-none')

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_crud.get_by_email(email)