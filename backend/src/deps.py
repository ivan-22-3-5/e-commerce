from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.users import UserCRUD
from src.db import models
from src.db.db import get_db
from src.utils import get_user_id_from_jwt

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/token")

TokenDep = Annotated[str, Depends(oauth2_schema)]

SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(token: TokenDep, db: SessionDep):
    return await UserCRUD.get(get_user_id_from_jwt(token), db)


CurrentUserDep = Annotated[models.User, Depends(get_current_user)]
