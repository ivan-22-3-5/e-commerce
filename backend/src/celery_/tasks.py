from celery import Celery

from .config import celery_config
from .utils import send_email

celery = Celery("celery", broker=celery_config.CELERY_BROKER_URL, backend=celery_config.CELERY_BACKEND_URL)


@celery.task
def send_password_recovery_email(username, link, email_address):
    send_email(email_address, subject="Password recovery", template_name="password_recovery.html",
               username=username, link=link)


@celery.task
def send_confirmation_code_email(code, email_address):
    send_email(email_address, subject="Confirmation code", template_name="confirmation_code.html",
               code=code)
