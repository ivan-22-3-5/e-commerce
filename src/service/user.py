from redis.asyncio import Redis

from src.config import rules
from src.crud import UserCRUD
from src.custom_exceptions import InvalidConfirmationCodeError, ResourceAlreadyExistsError, EmailNotConfirmedError
from src.db.models import User
from src.schemas.user import UserIn, GoogleUserInfo


class UserService:
    def __init__(self, user_crud: UserCRUD, redis: Redis):
        self.user_crud = user_crud
        self.redis = redis

    async def register_user(self, user: UserIn):
        confirmation_code = await self.redis.get(f"confirmation_code:{user.email}")
        # TODO: user.confirmation_code != 999999 is a backdoor, SHOULD BE REMOVED
        if user.confirmation_code != 999999:
            if confirmation_code is None or int(confirmation_code) != user.confirmation_code:
                raise InvalidConfirmationCodeError("Invalid confirmation code")
        await self.redis.delete(f"confirmation_code:{user.email}")

        return await self.user_crud.create(User(**user.model_dump(exclude={'confirmation_code'})))

    async def register_user_using_google(self, user: GoogleUserInfo):
        if (await self.user_crud.get_by_email(user.email)) is not None:
            raise ResourceAlreadyExistsError("Email already registered")

        if user.email_verified is False:
            raise EmailNotConfirmedError("Cannot register user with unverified email.")

        return await self.user_crud.create(User(
            identity_provider_id=user.id,
            email=user.email,
            password=None,
            name=user.name[:rules.MAX_USERNAME_LENGTH]
        ))

    async def get_user_by_identity_provider_id(self, identity_provider_id: str):
        return await self.user_crud.get_by_idp_id(identity_provider_id)

    async def get_user_by_id(self, user_id: int):
        return await self.user_crud.get(user_id)

    async def get_user_by_email(self, email: str):
        return await self.user_crud.get_by_email(email)
