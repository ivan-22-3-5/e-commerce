from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='src/.env', env_file_encoding='utf-8')

    TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    RECOVERY_TOKEN_EXPIRE_MINUTES: int
    CONFIRMATION_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str = "HS256"

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    PASSWORD_RECOVERY_LINK: str
    EMAIL_CONFIRMATION_LINK: str

    POSTGRESQL_DB_URL: str

    CORS_ORIGINS: list[str]

    SAME_SITE_COOKIE: Literal['strict', 'lax', 'none']

    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_PORT: int
    SMTP_MAIL: str
    SMTP_SERVER: str

    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: str


settings = Settings()
