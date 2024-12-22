from django.core.mail import send_mail
from django.conf import settings
from typing import List

def send_email(to: List[str], subject: str, message: str, from_email: str = None):
    """
    Sends an email with the specified subject and message to the given recipients.

    Args:
        to (List[str]): List of recipient email addresses.
        subject (str): Subject of the email.
        message (str): Plain-text body of the email.
    """
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        recipient_list=to,
        fail_silently=True,
    )
