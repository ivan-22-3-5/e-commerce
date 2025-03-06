from celery import Celery

from src.config import settings
from src.utils import send_email

celery = Celery("celery", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_BACKEND_URL)


@celery.task
def send_password_recovery_email(username, link, email_address):
    send_email(username, link, email_address, subject="Password recovery", template_name="password_recovery.html")


@celery.task
def send_email_confirmation_email(username, link, email_address):
    send_email(username, link, email_address, subject="Email confirmation", template_name="email_confirmation.html")
