import smtplib
from datetime import datetime, timedelta, UTC
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import stripe
from jinja2 import Environment, FileSystemLoader
from passlib.context import CryptContext
from jose import JWTError, ExpiredSignatureError, jwt

from src.config import settings
from src.custom_exceptions import InvalidTokenError
from src.db import models

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


def create_payment_intent(order: models.Order):
    amount = int(order.total_price * 100)
    automatic_payment_methods = {
        "enabled": True,
        "allow_redirects": 'never'
    }
    metadata = {
        "order_id": str(order.id),
        "user_id": str(order.user_id)
    }
    return stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",
        automatic_payment_methods=automatic_payment_methods,
        metadata=metadata,
        api_key=settings.STRIPE_SECRET_KEY
    )


def send_email(username: str, link: str, email_address: str, subject: str, template_name: str):
    env = Environment(loader=FileSystemLoader('src/html_templates'))
    template = env.get_template(template_name)
    html_content = template.render(username=username, link=link)

    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_MAIL
    msg['To'] = email_address
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
