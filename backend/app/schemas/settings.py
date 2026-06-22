"""Schemas (DTOs) das configurações administrativas — e-mail de disparo (SMTP)."""

from pydantic import BaseModel, EmailStr, Field

# Porta SMTP padrão (submission/STARTTLS).
DEFAULT_SMTP_PORT = 587
MAX_HOST_LENGTH = 255
MAX_SECRET_LENGTH = 512


class EmailSettingsUpdate(BaseModel):
    """Payload para configurar o e-mail de disparo no painel /admin.

    ``password`` é write-only: quando ausente/vazia, mantém a senha já salva
    (não é necessário reenviá-la a cada edição).
    """

    host: str = Field(min_length=1, max_length=MAX_HOST_LENGTH)
    port: int = Field(default=DEFAULT_SMTP_PORT, ge=1, le=65535)
    username: str = Field(default="", max_length=MAX_HOST_LENGTH)
    password: str | None = Field(default=None, max_length=MAX_SECRET_LENGTH)
    from_email: EmailStr
    from_name: str = Field(default="", max_length=MAX_HOST_LENGTH)
    use_tls: bool = True


class EmailSettingsPublic(BaseModel):
    """Configuração de e-mail exposta ao admin (NUNCA inclui a senha)."""

    host: str = ""
    port: int = DEFAULT_SMTP_PORT
    username: str = ""
    from_email: str = ""
    from_name: str = ""
    use_tls: bool = True
    # Indica se já existe uma senha salva (sem revelá-la).
    password_set: bool = False


class TestEmailRequest(BaseModel):
    """Solicitação de envio de e-mail de teste para validar o SMTP."""

    to: EmailStr
