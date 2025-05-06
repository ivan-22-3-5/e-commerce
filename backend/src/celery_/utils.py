import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

from .config import celery_config


def send_email(email_address: str, subject: str, template_name: str, **kwargs):
    env = Environment(loader=FileSystemLoader('src/celery_/email_templates'))
    template = env.get_template(template_name)
    html_content = template.render(**kwargs)

    msg = MIMEMultipart()
    msg['From'] = celery_config.SMTP_MAIL
    msg['To'] = email_address
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    with smtplib.SMTP(celery_config.SMTP_SERVER, celery_config.SMTP_PORT) as server:
        server.starttls()
        server.login(celery_config.SMTP_USERNAME, celery_config.SMTP_PASSWORD)
        server.send_message(msg)
