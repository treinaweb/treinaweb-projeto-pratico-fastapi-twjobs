from email.message import EmailMessage
from typing import Literal

import aiosmtplib
from pydantic import BaseModel

from .config import settings
from .template import render_template


class WelcomeEmailContext(BaseModel):
    name: str
    role: Literal["candidate", "company"]


class MailService:
    def __init__(self):
        self.from_mail = settings.EMAIL_FROM
        self.host = settings.EMAIL_HOST
        self.port = settings.EMAIL_PORT
        self.username = settings.EMAIL_USER
        self.password = settings.EMAIL_PASSWORD
        self.use_tls = settings.EMAIL_USE_TLS

    async def _send_html_mail(self, subject: str, to: str, html_content: str):
        message = EmailMessage()
        message["From"] = self.from_mail
        message["To"] = to
        message["Subject"] = subject

        message.set_content(
            "This email requires an HTML-compatible email client."
        )
        message.add_alternative(html_content, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls,
        )

    async def send_welcome_mail(self, to: str, context: WelcomeEmailContext):
        html_content = render_template(
            "email/welcome.html", context.model_dump()
        )
        await self._send_html_mail(
            subject="Bem-vindo ao TWJobs!", to=to, html_content=html_content
        )


mail_service = MailService()
