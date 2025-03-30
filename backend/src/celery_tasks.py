from celery import Celery

from src.config import settings
from src.utils import send_email

celery = Celery("celery", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_BACKEND_URL)


@celery.task
def send_password_recovery_email(username, link, email_address):
    send_email(email_address, subject="Password recovery", template_name="password_recovery.html",
               username=username, link=link)


@celery.task
def send_confirmation_code_email(code, email_address):
    send_email(email_address, subject="Confirmation code", template_name="confirmation_code.html",
               code=code)
