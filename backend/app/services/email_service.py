"""Envio de e-mails via SMTP.

A configuração de SMTP é resolvida em tempo de envio: usa o que o admin salvou
em /admin (banco) e, na ausência, faz fallback para o .env. Ver
:class:`~app.services.settings_service.SettingsService`.
"""

from email.message import EmailMessage

import aiosmtplib

from app.core.constants import (
    EMAIL_VERIFICATION_SUBJECT,
    PASSWORD_RESET_EMAIL_SUBJECT,
    TEST_EMAIL_SUBJECT,
)
from app.db.mongodb import get_database
from app.repositories.settings_repository import SettingsRepository
from app.services.settings_service import EmailConfig, SettingsService


async def _effective_config() -> EmailConfig:
    """Resolve a configuração de SMTP em uso (banco -> .env)."""
    service = SettingsService(SettingsRepository(get_database()))
    return await service.get_effective_email_config()


async def _send_email(to_email: str, subject: str, text_body: str, html_body: str) -> None:
    """Monta e envia um e-mail multipart via SMTP usando a config efetiva."""
    config = await _effective_config()

    message = EmailMessage()
    message["From"] = f"{config.from_name} <{config.from_email}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    # Auth/TLS são opcionais: ausentes em desenvolvimento (Mailpit), obrigatórios
    # na maioria dos provedores de produção (STARTTLS + usuário/senha).
    options: dict[str, object] = {"hostname": config.host, "port": config.port}
    if config.use_tls:
        options["start_tls"] = True
    if config.username:
        options["username"] = config.username
        options["password"] = config.password

    await aiosmtplib.send(message, **options)


async def send_test_email(to_email: str) -> None:
    """Envia um e-mail de teste para validar a configuração de SMTP do /admin."""
    await _send_email(
        to_email,
        TEST_EMAIL_SUBJECT,
        (
            "Este é um e-mail de teste do Papo Dev Web.\n\n"
            "Se você recebeu esta mensagem, o e-mail de disparo está configurado "
            "corretamente."
        ),
        """
        <p>Este é um <strong>e-mail de teste</strong> do Papo Dev Web.</p>
        <p>Se você recebeu esta mensagem, o e-mail de disparo está configurado
        corretamente. ✅</p>
        """,
    )


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
