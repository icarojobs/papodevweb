"""Serviço de configurações da plataforma — e-mail de disparo (SMTP).

A senha do SMTP é guardada criptografada (Fernet) e nunca é devolvida pela API
(write-only). A configuração efetiva usada para enviar e-mails prefere o que foi
salvo no banco pelo admin e, na ausência, faz fallback para as variáveis de
ambiente (.env).
"""

from dataclasses import dataclass
from typing import Any

from app.core.config import get_settings
from app.core.constants import EMAIL_SETTINGS_KEY
from app.core.crypto import decrypt_secret, encrypt_secret
from app.repositories.settings_repository import SettingsRepository
from app.schemas.settings import DEFAULT_SMTP_PORT, EmailSettingsPublic, EmailSettingsUpdate


@dataclass(frozen=True)
class EmailConfig:
    """Configuração efetiva de SMTP usada para enviar e-mails."""

    host: str
    port: int
    username: str
    password: str
    from_email: str
    from_name: str
    use_tls: bool


class SettingsService:
    """Regras de leitura/escrita das configurações de e-mail de disparo."""

    def __init__(self, repository: SettingsRepository) -> None:
        self._repository = repository

    async def get_email_settings(self) -> EmailSettingsPublic:
        """Configuração de e-mail para exibição no /admin (sem a senha)."""
        document = await self._repository.get(EMAIL_SETTINGS_KEY)
        if not document:
            return EmailSettingsPublic()
        return EmailSettingsPublic(
            host=document.get("host", ""),
            port=document.get("port", DEFAULT_SMTP_PORT),
            username=document.get("username", ""),
            from_email=document.get("from_email", ""),
            from_name=document.get("from_name", ""),
            use_tls=document.get("use_tls", True),
            password_set=bool(document.get("password_encrypted")),
        )

    async def update_email_settings(self, update: EmailSettingsUpdate) -> EmailSettingsPublic:
        """Salva a configuração de e-mail. Mantém a senha atual se não enviada."""
        values: dict[str, Any] = {
            "host": update.host,
            "port": update.port,
            "username": update.username,
            "from_email": str(update.from_email),
            "from_name": update.from_name,
            "use_tls": update.use_tls,
        }
        # Senha write-only: só atualiza (criptografando) quando uma nova é enviada.
        if update.password:
            values["password_encrypted"] = encrypt_secret(update.password)

        await self._repository.upsert(EMAIL_SETTINGS_KEY, values)
        return await self.get_email_settings()

    async def get_effective_email_config(self) -> EmailConfig:
        """Configuração de SMTP em uso: banco (se configurado) ou .env (fallback)."""
        settings = get_settings()
        document = await self._repository.get(EMAIL_SETTINGS_KEY)
        if not document or not document.get("host"):
            return EmailConfig(
                host=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_user,
                password=settings.smtp_password,
                from_email=settings.smtp_from,
                from_name=settings.smtp_from_name,
                use_tls=settings.smtp_use_tls,
            )
        encrypted = document.get("password_encrypted")
        password = (decrypt_secret(encrypted) if encrypted else "") or ""
        return EmailConfig(
            host=document["host"],
            port=document.get("port", DEFAULT_SMTP_PORT),
            username=document.get("username", ""),
            password=password,
            from_email=document.get("from_email") or settings.smtp_from,
            from_name=document.get("from_name") or settings.smtp_from_name,
            use_tls=document.get("use_tls", True),
        )
