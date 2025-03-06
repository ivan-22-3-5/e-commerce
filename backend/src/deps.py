from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.users import UserCRUD
from src.db import models
from src.db.db import get_db
from src.utils import get_user_id_from_jwt

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/token")

token_dependency = Annotated[str, Depends(oauth2_schema)]

db_dependency = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(token: token_dependency, db: db_dependency):
    return await UserCRUD.get(get_user_id_from_jwt(token), db)


cur_user_dependency = Annotated[models.User, Depends(get_current_user)]
