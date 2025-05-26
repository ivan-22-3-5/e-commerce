from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis  # Changed from redis to redis.asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from aiohttp import ClientSession

from src.clients.http_client import get_http_client
from src.clients.redis_client import get_redis_client
from src.config import settings
from src.crud import (
    CartItemCRUD,
    ProductCRUD,
    CategoryCRUD,
    OrderCRUD,
    RefreshTokenCRUD,
    RecoveryTokenCRUD,
)
from src.crud.users import UserCRUD
from src.db import models
from src.db.db import get_db
from src.file_storage import FileStorage, local_file_storage
from src.logger import logger
from src.schemas.user import GoogleUserInfo
from src.service.cart import CartService
from src.service.category import CategoryService
from src.service.order import OrderService
from src.service.product import ProductService
from src.service.token import TokenService
from src.service.user import UserService
from src.service.review import ReviewService
from src.utils import get_user_id_from_jwt

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

TokenDep = Annotated[str, Depends(oauth2_schema)]
SessionDep = Annotated[AsyncSession, Depends(get_db)]
FileStorageDep = Annotated[FileStorage, Depends(lambda: local_file_storage)]
HTTPClientDep = Annotated[ClientSession, Depends(get_http_client)]


async def get_access_token(code: str, http: HTTPClientDep) -> str:
    async with http.post(
        settings.GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URL,
            "grant_type": "authorization_code",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ) as response:
        if response.status != 200:
            logger.error(
                f"Failed to get access token from Google: {await response.text()}"
            )
            # Consider raising an exception here
            raise Exception("Failed to get access token from Google")

        data = await response.json()
        access_token = data.get("access_token")
        if not access_token:
            logger.error(f"No access_token in Google response: {data}")
            raise Exception("No access_token in Google response")
        return access_token


GoogleAccessTokenDep = Annotated[str, Depends(get_access_token)]


async def get_google_user_info(
    access_token: GoogleAccessTokenDep, http: HTTPClientDep
) -> GoogleUserInfo:
    async with (
        http.get(
            settings.GOOGLE_USER_INFO_URL,  # Changed to GET as per common practice for userinfo
            headers={"Authorization": f"Bearer {access_token}"},
        ) as response
    ):
        if response.status != 200:
            logger.error(
                f"Failed to get user info from Google: {await response.text()}"
            )
            raise Exception("Failed to get user info from Google")

        return GoogleUserInfo(**(await response.json()))


GoogleUserInfoDep = Annotated[GoogleUserInfo, Depends(get_google_user_info)]
RedisClientDep = Annotated[Redis, Depends(get_redis_client)]


def get_cart_service(db: SessionDep) -> CartService:
    return CartService(CartItemCRUD(db), ProductCRUD(db))


CartServiceDep = Annotated[CartService, Depends(get_cart_service)]


def get_category_service(db: SessionDep) -> CategoryService:
    return CategoryService(CategoryCRUD(db), ProductCRUD(db))


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]


def get_order_service(db: SessionDep) -> OrderService:
    return OrderService(OrderCRUD(db), CartItemCRUD(db), ProductCRUD(db))


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


def get_product_service(db: SessionDep, file_storage: FileStorageDep) -> ProductService:
    return ProductService(ProductCRUD(db), file_storage)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]


def get_user_service(db: SessionDep, redis: RedisClientDep) -> UserService:
    return UserService(UserCRUD(db), redis)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_token_service(db: SessionDep) -> TokenService:
    return TokenService(RefreshTokenCRUD(db), RecoveryTokenCRUD(db))


TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


def get_review_service(db: SessionDep) -> ReviewService:
    return ReviewService(db)


ReviewServiceDep = Annotated[ReviewService, Depends(get_review_service)]


async def get_current_user(
    token: TokenDep, user_service: UserServiceDep
) -> models.User:
    user_id = get_user_id_from_jwt(token)
    user = await user_service.get_user_by_id(user_id)
    if (
        user is None
    ):  # Should be handled by get_user_id_from_jwt or user_service.get_user_by_id
        raise Exception(
            "User not found, this should not happen if token is valid"
        )  # Or a specific exception
    return user


CurrentUserDep = Annotated[models.User, Depends(get_current_user)]
