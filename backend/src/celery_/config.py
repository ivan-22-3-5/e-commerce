from pydantic_settings import BaseSettings


class CeleryConfig(BaseSettings):
    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: str

    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_PORT: int
    SMTP_MAIL: str
    SMTP_SERVER: str


celery_config = CeleryConfig()
