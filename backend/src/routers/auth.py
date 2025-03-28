from datetime import timedelta, datetime, UTC
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.crud import RefreshTokenCRUD, RecoveryTokenCRUD, UserCRUD
from src.custom_exceptions import InvalidCredentialsError, InvalidTokenError, ResourceDoesNotExistError, \
    ResourceAlreadyExistsError
from src.db.models import RefreshToken, RecoveryToken, User
from src.deps import TokenDep, SessionDep, GoogleUserInfoDep
from src.schemas.message import Message
from src.schemas.new_password import NewPasswordIn
from src.schemas.token import Token
from src.utils import create_jwt_token, get_user_id_from_jwt, verify_password

router = APIRouter(
    prefix='/auth',
    tags=["Authentication"]
)


async def handle_user_tokens(user_id: int, response: Response, db: AsyncSession):
    access_token = create_jwt_token(user_id=user_id,
                                    expires_in=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_jwt_token(user_id=user_id,
                                     expires_in=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    await RefreshTokenCRUD.upsert(RefreshToken(user_id=user_id, token=refresh_token), db)
    response.set_cookie(key="refresh_token",
                        value=refresh_token,
                        httponly=True,
                        secure=False,  # should be True in production
                        expires=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                        samesite=settings.SAME_SITE_COOKIE)
    return {'access_token': access_token, "token_type": "bearer"}


@router.get('/google', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def authenticate_with_google():
    return RedirectResponse(url=
                            f"{settings.GOOGLE_AUTH_URL}"
                            f"?client_id={settings.GOOGLE_CLIENT_ID}"
                            f"&redirect_uri={settings.GOOGLE_REDIRECT_URL}"
                            f"&response_type=code"
                            f"&scope=openid email profile")


@router.get('/google/callback', status_code=status.HTTP_200_OK)
async def google_callback(res: Response, google_user: GoogleUserInfoDep, db: SessionDep):
    # user already registered with an Identity Provider
    if (user := await UserCRUD.get_by_idp_id(google_user.id, db)) is not None:
        return await handle_user_tokens(user.id, res, db)

    # user already registered without an Identity Provider
    if (await UserCRUD.get_by_email(google_user.email, db)) is not None:
        raise ResourceAlreadyExistsError("Email already registered")

    # new user handling
    new_user = await UserCRUD.create(User(
        identity_provider_id=google_user.id,
        email=google_user.email,
        is_email_verified=google_user.email_verified,
        password=None,
        name=google_user.name  # TODO: check if within length bounds
    ), db=db)

    return await handle_user_tokens(new_user.id, res, db)


@router.post('/login', status_code=status.HTTP_200_OK, response_model=Token)
async def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep, res: Response):
    user = await UserCRUD.get_by_email(user_credentials.username, db)
    if user.password is None:
        raise InvalidCredentialsError("Account is registered with an external provider")

    if not (user and verify_password(user_credentials.password, user.password)):
        raise InvalidCredentialsError("No account with the given email exists or the password is wrong")

    return await handle_user_tokens(user.id, res, db)


@router.post('/refresh', status_code=status.HTTP_200_OK, response_model=Token)
async def refresh(req: Request, res: Response, db: SessionDep):
    token = req.cookies.get('refresh_token')
    if not token:
        raise InvalidTokenError("No token found")
    user_id = get_user_id_from_jwt(token)
    db_token = await RefreshTokenCRUD.get(user_id, db, on_not_found='return-none')
    if not (db_token and db_token.token == token):
        raise InvalidTokenError("Invalid refresh token")

    return await handle_user_tokens(user_id, res, db)


@router.post('/password-recovery/{email}', status_code=status.HTTP_200_OK, response_model=Message)
async def recover_password(email: EmailStr, db: SessionDep):
    if (user := await UserCRUD.get_by_email(email, db)) is None:
        raise ResourceDoesNotExistError("The given email is not registered yet")
    recovery_token = create_jwt_token(user_id=user.id,
                                      expires_in=timedelta(minutes=settings.RECOVERY_TOKEN_EXPIRE_MINUTES))
    await RecoveryTokenCRUD.upsert(RecoveryToken(user_id=user.id,
                                                 token=recovery_token), db)
    # send_password_recovery_email.delay(username=user.username,
    #                                    link=settings.PASSWORD_RECOVERY_LINK + recovery_token,
    #                                    email_address=email)
    return Message(message="Recovery email sent")


@router.post('/reset-password', status_code=status.HTTP_200_OK, response_model=Message)
async def reset_password(new_password: NewPasswordIn, db: SessionDep):
    user_id = get_user_id_from_jwt(new_password.token)
    db_token = await RecoveryTokenCRUD.get(user_id, db, on_not_found='return-none')
    if not (db_token and db_token.token == new_password.token):
        raise InvalidTokenError("Invalid recovery token")
    user = await UserCRUD.get(user_id, db)
    user.password = new_password

    await RecoveryTokenCRUD.delete(user_id, db)
    return Message(message="New password set")


@router.post('/logout', status_code=status.HTTP_200_OK, response_model=Message)
async def refresh(token: TokenDep, res: Response, db: SessionDep):
    user_id = get_user_id_from_jwt(token)
    await RefreshTokenCRUD.delete(user_id, db=db)
    res.delete_cookie('refresh_token')
    return Message(message='logged out')
