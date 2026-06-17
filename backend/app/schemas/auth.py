"""Schemas (DTOs) de autenticação validados via Pydantic."""

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.core.constants import (
    ERR_PASSWORDS_DO_NOT_MATCH,
    MAX_FULL_NAME_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_FULL_NAME_LENGTH,
    MIN_PASSWORD_LENGTH,
)
from app.schemas.user import UserPublic


class RegisterRequest(BaseModel):
    """Payload de cadastro: Nome Completo, E-mail, Senha e Repetir senha."""

    full_name: str = Field(min_length=MIN_FULL_NAME_LENGTH, max_length=MAX_FULL_NAME_LENGTH)
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError(ERR_PASSWORDS_DO_NOT_MATCH)
        return self


class LoginRequest(BaseModel):
    """Payload de login: E-mail e Senha."""

    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """Resposta de autenticação: access token + dados públicos do usuário."""

    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class ForgotPasswordRequest(BaseModel):
    """Solicitação de redefinição de senha."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Redefinição de senha a partir de um token enviado por e-mail."""

    token: str = Field(min_length=1)
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> "ResetPasswordRequest":
        if self.password != self.confirm_password:
            raise ValueError(ERR_PASSWORDS_DO_NOT_MATCH)
        return self


class VerifyEmailRequest(BaseModel):
    """Confirmação de e-mail a partir de um token enviado por e-mail."""

    token: str = Field(min_length=1)


class MessageResponse(BaseModel):
    """Resposta simples com uma mensagem."""

    message: str
