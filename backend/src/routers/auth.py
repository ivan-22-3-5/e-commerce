from datetime import timedelta, datetime, UTC
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from src.config import settings
from src.custom_exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    ResourceDoesNotExistError,
    ResourceAlreadyExistsError,
)
from src.deps import TokenDep, GoogleUserInfoDep, RedisClientDep, TokenServiceDep, UserServiceDep
from src.schemas.message import Message
from src.schemas.new_password import NewPasswordIn
from src.schemas.token import Token
from src.schemas.user import UserIn, UserOut
from src.service.token import TokenService
from src.utils import create_jwt_token, get_user_id_from_jwt, verify_password, generate_confirmation_code
from src.celery_.tasks import send_password_recovery_email, send_confirmation_code_email

router = APIRouter(
    prefix='/auth',
    tags=["Authentication"]
)


async def _handle_user_tokens(user_id: int, response: Response, token_service: TokenService):
    access_token = create_jwt_token(user_id=user_id,
                                    expires_in=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES))
    refresh_token = create_jwt_token(user_id=user_id,
                                     expires_in=timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS))
    await token_service.upsert_refresh_token(user_id, refresh_token)

    response.set_cookie(key="refresh_token",
                        value=refresh_token,
                        httponly=True,
                        secure=False,  # should be True in production
                        expires=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS),
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
async def google_callback(res: Response,
                          google_user: GoogleUserInfoDep,
                          user_service: UserServiceDep,
                          token_service: TokenServiceDep):
    if (user := await user_service.get_user_by_identity_provider_id(google_user.id)) is None:
        user = await user_service.register_user_using_google(google_user)

    return await _handle_user_tokens(user.id, res, token_service)


@router.post('/{email}/send_confirmation_code', status_code=status.HTTP_200_OK, response_model=Message)
async def send_confirmation_code(email: EmailStr, user_service: UserServiceDep, redis: RedisClientDep):
    if await user_service.get_user_by_email(email):
        raise ResourceAlreadyExistsError("Email is already registered")
    confirmation_code = generate_confirmation_code()
    await redis.set(f"confirmation_code:{email}",
                    confirmation_code,
                    ex=settings.CONFIRMATION_CODE_EXPIRATION_SECONDS)
    send_confirmation_code_email.delay(code=confirmation_code,
                                       email_address=email)
    return Message(message="Confirmation code sent")


@router.post('/register', status_code=status.HTTP_200_OK, response_model=UserOut)
async def register(user: UserIn, user_service: UserServiceDep):
    return await user_service.register_user(user)


@router.post('/login', status_code=status.HTTP_200_OK, response_model=Token)
async def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
                res: Response,
                user_service: UserServiceDep,
                token_service: TokenServiceDep):
    user = await user_service.get_user_by_email(user_credentials.username)
    if user is not None and user.password is None:
        raise InvalidCredentialsError("Account is registered with an external provider")

    if not (user and verify_password(user_credentials.password, user.password)):
        raise InvalidCredentialsError("No account with the given email exists or the password is wrong")

    return await _handle_user_tokens(user.id, res, token_service)


@router.post('/refresh', status_code=status.HTTP_200_OK, response_model=Token)
async def refresh(req: Request, res: Response, token_service: TokenServiceDep):
    token = req.cookies.get('refresh_token')
    if not token:
        raise InvalidTokenError("No token found")
    user_id = get_user_id_from_jwt(token)

    if (await token_service.is_refresh_token_valid(user_id, token)) is False:
        raise InvalidTokenError("Invalid refresh token")

    return await _handle_user_tokens(user_id, res, token_service)


@router.post('/password-recovery/{email}', status_code=status.HTTP_200_OK, response_model=Message)
async def recover_password(email: EmailStr, user_service: UserServiceDep, token_service: TokenServiceDep):
    if (user := await user_service.get_user_by_email(email)) is None:
        raise ResourceDoesNotExistError("The given email is not registered yet")

    recovery_token = create_jwt_token(user_id=user.id,
                                      expires_in=timedelta(minutes=settings.RECOVERY_TOKEN_EXPIRATION_MINUTES))

    await token_service.upsert_recovery_token(user.id, recovery_token)

    send_password_recovery_email.delay(username=user.username,
                                       link=recovery_token,
                                       email_address=email)
    return Message(message="Recovery email sent")


@router.put('/me/password/', status_code=status.HTTP_200_OK, response_model=Message)
async def reset_password(new_password: NewPasswordIn, token_service: TokenServiceDep, user_service: UserServiceDep):
    user_id = get_user_id_from_jwt(new_password.token)

    if (await token_service.is_recovery_token_valid(user_id, new_password.token)) is False:
        raise InvalidTokenError("Invalid recovery token")

    user = await user_service.get_user(user_id)
    user.password = new_password

    await token_service.revoke_recovery_token(user_id)
    return Message(message="New password set")


@router.post('/logout', status_code=status.HTTP_200_OK, response_model=Message)
async def logout(token: TokenDep, res: Response, token_service: TokenServiceDep):
    user_id = get_user_id_from_jwt(token)
    await token_service.revoke_refresh_token(user_id)
    res.delete_cookie('refresh_token')
    return Message(message='logged out')
