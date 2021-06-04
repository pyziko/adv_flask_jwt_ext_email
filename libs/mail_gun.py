import os
from typing import List

from requests import Response, post
from libs.strings import getText


class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN", None)  # can be None
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", None)  # can be None
    FROM_TITLE = "Stores REST API"
    FROM_EMAIL = os.environ.get("FROM_EMAIL")

    @classmethod
    def send_confirmation_email(cls, email: List[str], subject: str, text: str, html: str) -> Response:
        if cls.MAILGUN_DOMAIN is None:
            raise MailGunException(getText("mailgun_failed_load_domain"))

        if cls.MAILGUN_API_KEY is None:
            raise MailGunException(getText("mailgun_failed_load_domain"))

        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html
            }
        )

        if response.status_code != 200:
            raise MailGunException(getText("mailgun_error_sending_email"))

        return response
