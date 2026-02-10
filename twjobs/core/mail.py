from email.message import EmailMessage
from typing import Literal

import aiosmtplib
from pydantic import BaseModel

from .config import settings
from .template import render_template


class WelcomeEmailContext(BaseModel):
    name: str
    role: Literal["candidate", "company"]


class ApplicationConfirmationContext(BaseModel):
    candidate_name: str
    job_title: str
    company_name: str
    job_level: str
    employment_type: str
    location: str
    is_remote: bool


class ApplicationStatusUpdateContext(BaseModel):
    candidate_name: str
    job_title: str
    company_name: str
    job_level: str
    employment_type: str
    status: Literal["reviewing", "approved", "rejected"]


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

    async def send_application_confirmation_mail(
        self, to: str, context: ApplicationConfirmationContext
    ):
        html_content = render_template(
            "email/application_confirmation.html", context.model_dump()
        )
        await self._send_html_mail(
            subject="Confirmação de candidatura - TWJobs",
            to=to,
            html_content=html_content,
        )

    async def send_application_status_update_mail(
        self, to: str, context: ApplicationStatusUpdateContext
    ):
        status_titles = {
            "reviewing": "Em análise",
            "approved": "Aprovada",
            "rejected": "Não Aprovada",
        }

        html_content = render_template(
            "email/application_status_update.html", context.model_dump()
        )

        await self._send_html_mail(
            subject=(
                f"Candidatura {status_titles[context.status]} - "
                f"{context.job_title}"
            ),
            to=to,
            html_content=html_content,
        )


mail_service = MailService()
