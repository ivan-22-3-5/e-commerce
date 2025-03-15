from datetime import timedelta, datetime, UTC
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from src.celery_tasks import send_password_recovery_email
from src.custom_exceptions import InvalidCredentialsError, InvalidTokenError, ResourceDoesNotExistError
from src.db.models import RefreshToken, RecoveryToken
from src.schemas.new_password import NewPasswordIn
from src.schemas.token import Token
from src.schemas.message import Message
from src.crud import RefreshTokenCRUD, RecoveryTokenCRUD, UserCRUD
from src.config import settings
from src.deps import token_dependency, db_dependency
from src.utils import create_jwt_token, get_user_id_from_jwt, verify_password

router = APIRouter(
    prefix='/auth',
    tags=["Authentication"]
)


@router.post('/token', status_code=status.HTTP_200_OK, response_model=Token)
async def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency,
                response: Response):
    user = await UserCRUD.get_by_email(user_credentials.username, db)
    if not (user and verify_password(user_credentials.password, user.password)):
        raise InvalidCredentialsError("No account with the given email exists or the password is wrong")
    access_token = create_jwt_token(user_id=user.id,
                                    expires_in=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_jwt_token(user_id=user.id,
                                     expires_in=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    await RefreshTokenCRUD.upsert(RefreshToken(user_id=user.id, token=refresh_token), db)
    response.set_cookie(key="refresh_token",
                        value=refresh_token,
                        httponly=True,
                        secure=False,
                        expires=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                        samesite=settings.SAME_SITE_COOKIE)
    return {'access_token': access_token, "token_type": "bearer"}


@router.post('/refresh', status_code=status.HTTP_200_OK, response_model=Token)
async def refresh(req: Request, res: Response, db: db_dependency):
    token = req.cookies.get('refresh_token')
    if not token:
        raise InvalidTokenError("No token found")
    user_id = get_user_id_from_jwt(token)
    db_token = await RefreshTokenCRUD.get(user_id, db, on_not_found='return-none')
    if not (db_token and db_token.token == token):
        raise InvalidTokenError("Invalid refresh token")
    access_token = create_jwt_token(user_id=user_id,
                                    expires_in=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_jwt_token(user_id=user_id,
                                     expires_in=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    await RefreshTokenCRUD.update(user_id, RefreshToken(user_id=user_id, token=refresh_token), db=db)
    res.set_cookie(key="refresh_token",
                   value=refresh_token,
                   httponly=True,
                   secure=False,
                   expires=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                   samesite=settings.SAME_SITE_COOKIE)
    return {'access_token': access_token, "token_type": "bearer"}


@router.post('/password-recovery/{email}', status_code=status.HTTP_200_OK, response_model=Message)
async def recover_password(email: EmailStr, db: db_dependency):
    if (user := await UserCRUD.get_by_email(email, db)) is None:
        raise ResourceDoesNotExistError("The given email is not registered yet")
    recovery_token = create_jwt_token(user_id=user.id,
                                      expires_in=timedelta(minutes=settings.RECOVERY_TOKEN_EXPIRE_MINUTES))
    await RecoveryTokenCRUD.upsert(RecoveryToken(user_id=user.id,
                                                 token=recovery_token), db)
    send_password_recovery_email.delay(username=user.username,
                                       link=settings.PASSWORD_RECOVERY_LINK + recovery_token,
                                       email_address=email)
    return Message(message="Recovery email sent")


@router.post('/reset-password', status_code=status.HTTP_200_OK, response_model=Message)
async def reset_password(new_password: NewPasswordIn, db: db_dependency):
    user_id = get_user_id_from_jwt(new_password.token)
    db_token = await RecoveryTokenCRUD.get(user_id, db, on_not_found='return-none')
    if not (db_token and db_token.token == new_password.token):
        raise InvalidTokenError("Invalid recovery token")
    user = await UserCRUD.get(user_id, db)
    user.password = new_password

    await RecoveryTokenCRUD.delete(user_id, db)
    return Message(message="New password set")


@router.post('/logout', status_code=status.HTTP_200_OK, response_model=Message)
async def refresh(token: token_dependency, res: Response, db: db_dependency):
    user_id = get_user_id_from_jwt(token)
    await RefreshTokenCRUD.delete(user_id, db=db)
    res.delete_cookie('refresh_token')
    return Message(message='logged out')
