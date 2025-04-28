from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Rules(BaseSettings):
    MAX_IMAGES_PER_PRODUCT: int = 10
    MAX_USERNAME_LENGTH: int = 50
    MIN_USERNAME_LENGTH: int = 3
    MIN_PASSWORD_LENGTH: int = 8
    MAX_HASHED_PASSWORD_LENGTH: int = 72
    MAX_CATEGORY_NAME_LENGTH: int = 30
    MAX_PRODUCT_TITLE_LENGTH: int = 30
    MAX_PRODUCT_DESCRIPTION_LENGTH: int = 1000
    MAX_REVIEW_CONTENT_LENGTH: int = 1000

    CONFIRMATION_CODE_LENGTH: int = 6
    CONFIRMATION_CODE_LOWER_BOUND: int = 10 ** (CONFIRMATION_CODE_LENGTH - 1)
    CONFIRMATION_CODE_UPPER_BOUND: int = 10 ** CONFIRMATION_CODE_LENGTH - 1


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='src/.env', env_file_encoding='utf-8')

    TOKEN_SECRET_KEY: str

    ACCESS_TOKEN_EXPIRATION_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 15
    RECOVERY_TOKEN_EXPIRATION_MINUTES: int = 15

    CONFIRMATION_CODE_EXPIRATION_SECONDS: int = 15 * 60
    ALGORITHM: str = "HS256"

    MAX_IMAGES_PER_PRODUCT: int = 10
    FILE_SIZE_LIMIT: int = 10 * 1024 * 1024
    SUPPORTED_IMAGE_TYPES: list[str] = ['image/jpeg', 'image/png']
    FILES_DIR: str = 'static/product_images'
    IMAGES_HOST: str = 'http://localhost:8000'
    IMAGES_BASE_PATH: str = '/static/product_images/'
    IMAGES_BASE_URL: str = IMAGES_HOST + IMAGES_BASE_PATH

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    PAYMENT_SUCCESS_REDIRECT_URL: str = 'http://localhost:8000/payment/success'

    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL: str = "https://www.googleapis.com/oauth2/v3/userinfo"
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URL: str

    PASSWORD_RECOVERY_LINK: str

    POSTGRESQL_DB_URL: str

    CORS_ORIGINS: list[str]

    SAME_SITE_COOKIE: Literal['strict', 'lax', 'none']

    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_PORT: int
    SMTP_MAIL: str
    SMTP_SERVER: str

    REDIS_HOST: str
    REDIS_PORT: int

    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: str


settings = Settings()
rules = Rules()
