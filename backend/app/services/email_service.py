"""Envio de e-mails via SMTP (Mailpit em desenvolvimento)."""

from email.message import EmailMessage

import aiosmtplib

from app.core.config import get_settings
from app.core.constants import EMAIL_VERIFICATION_SUBJECT, PASSWORD_RESET_EMAIL_SUBJECT


async def _send_email(to_email: str, subject: str, text_body: str, html_body: str) -> None:
    """Monta e envia um e-mail multipart via SMTP."""
    settings = get_settings()

    message = EmailMessage()
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    await aiosmtplib.send(message, hostname=settings.smtp_host, port=settings.smtp_port)


async def send_email_verification_email(to_email: str, verify_link: str) -> None:
    """Envia o e-mail de confirmação de conta (link válido por 24 horas)."""
    await _send_email(
        to_email,
        EMAIL_VERIFICATION_SUBJECT,
        (
            "Bem-vindo(a) ao Papo Dev Web!\n\n"
            f"Confirme o seu e-mail para ativar a conta:\n{verify_link}\n\n"
            "O link é válido por 24 horas. Se você não fez este cadastro, ignore este e-mail."
        ),
        f"""
        <p>Bem-vindo(a) ao <strong>Papo Dev Web</strong>!</p>
        <p><a href="{verify_link}">Clique aqui para confirmar o seu e-mail</a> e ativar a conta.</p>
        <p>O link é válido por <strong>24 horas</strong>. Se você não fez este cadastro, ignore.</p>
        """,
    )


async def send_password_reset_email(to_email: str, reset_link: str) -> None:
    """Envia o e-mail com o link de redefinição de senha."""
    await _send_email(
        to_email,
        PASSWORD_RESET_EMAIL_SUBJECT,
        (
            "Recebemos um pedido para redefinir a sua senha no Papo Dev Web.\n\n"
            f"Acesse o link a seguir para criar uma nova senha:\n{reset_link}\n\n"
            "Se você não solicitou, ignore este e-mail."
        ),
        f"""
        <p>Recebemos um pedido para redefinir a sua senha no <strong>Papo Dev Web</strong>.</p>
        <p><a href="{reset_link}">Clique aqui para criar uma nova senha</a>.</p>
        <p>Se você não solicitou, ignore este e-mail.</p>
        """,
    )
