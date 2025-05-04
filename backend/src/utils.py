import random
from datetime import datetime, timedelta, UTC

from passlib.context import CryptContext
from jose import JWTError, ExpiredSignatureError, jwt

from src.config import settings, rules
from src.custom_exceptions import InvalidTokenError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pass(password: str):
    return pwd_context.hash(password)


def verify_password(raw_password: str, hashed_password: str):
    return pwd_context.verify(raw_password, hashed_password)


def create_jwt_token(*, user_id: int, expires_in: timedelta):
    data_to_encode = {
        "sub": str(user_id),
        "exp": datetime.now(UTC) + expires_in
    }
    return jwt.encode(data_to_encode, settings.TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)


def get_user_id_from_jwt(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get('sub')
        if user_id is None:
            raise InvalidTokenError("Could not validate the token", {"WWW-Authenticate": "Bearer {}"})
    except ExpiredSignatureError:
        raise InvalidTokenError("The token has expired", {"WWW-Authenticate": "Bearer"})
    except JWTError:
        raise InvalidTokenError("Could not validate the token", {"WWW-Authenticate": "Bearer {}"})
    return int(user_id)


def generate_confirmation_code():
    return random.randint(rules.CONFIRMATION_CODE_LOWER_BOUND,
                          rules.CONFIRMATION_CODE_UPPER_BOUND)
