from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from aiohttp import ClientSession

from src.config import settings
from src.crud.users import UserCRUD
from src.db import models
from src.db.db import get_db
from src.file_storage import FileStorage, local_file_storage
from src.schemas.user import GoogleUserInfo
from src.utils import get_user_id_from_jwt

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

TokenDep = Annotated[str, Depends(oauth2_schema)]

SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(token: TokenDep, db: SessionDep):
    return await UserCRUD.get(get_user_id_from_jwt(token), db)


async def get_http_client():
    async with ClientSession() as session:
        yield session


CurrentUserDep = Annotated[models.User, Depends(get_current_user)]

FileStorageDep = Annotated[FileStorage, Depends(lambda: local_file_storage)]

HTTPClientDep = Annotated[ClientSession, Depends(get_http_client)]


async def get_access_token(code: str, http: HTTPClientDep) -> str:
    async with http.post(settings.GOOGLE_TOKEN_URL,
                         data={
                             "code": code,
                             "client_id": settings.GOOGLE_CLIENT_ID,
                             "client_secret": settings.GOOGLE_CLIENT_SECRET,
                             "redirect_uri": settings.GOOGLE_REDIRECT_URL,
                             "grant_type": "authorization_code",
                         },
                         headers={"Content-Type": "application/x-www-form-urlencoded"}) as response:
        if response.status != 200:
            ...
            # TODO: handle unsuccessful status

        return (await response.json()).get("access_token")


GoogleAccessTokenDep = Annotated[str, Depends(get_access_token)]


async def get_google_user_info(access_token: GoogleAccessTokenDep, http: HTTPClientDep) -> GoogleUserInfo:
    async with http.post(settings.GOOGLE_USER_INFO_URL,
                         headers={"Authorization": f"Bearer {access_token}"}) as response:
        if response.status != 200:
            ...
            # TODO: handle unsuccessful status

        return GoogleUserInfo(**(await response.json()))


GoogleUserInfoDep = Annotated[GoogleUserInfo, Depends(get_google_user_info)]
