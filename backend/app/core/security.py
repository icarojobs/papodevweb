"""Funções de segurança: hashing de senha (Argon2) e emissão/validação de JWT."""

from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import get_settings
from app.core.constants import JWT_ALGORITHM, TokenType

_password_hasher = PasswordHasher()


def hash_password(plain_password: str) -> str:
    """Gera o hash Argon2 de uma senha em texto puro."""
    return _password_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro corresponde ao hash armazenado."""
    try:
        return _password_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, get_settings().jwt_secret_key, algorithm=JWT_ALGORITHM)


def create_access_token(subject: str) -> str:
    """Cria um access token de curta duração."""
    settings = get_settings()
    return _create_token(
        subject,
        TokenType.ACCESS,
        timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )


def create_refresh_token(subject: str) -> str:
    """Cria um refresh token de longa duração."""
    settings = get_settings()
    return _create_token(
        subject,
        TokenType.REFRESH,
        timedelta(days=settings.jwt_refresh_token_expire_days),
    )


def create_password_reset_token(subject: str) -> str:
    """Cria um token de redefinição de senha (curta duração)."""
    settings = get_settings()
    return _create_token(
        subject,
        TokenType.RESET,
        timedelta(minutes=settings.jwt_reset_token_expire_minutes),
    )


def create_email_verification_token(subject: str) -> str:
    """Cria um token de confirmação de e-mail (válido por até 24 horas)."""
    settings = get_settings()
    return _create_token(
        subject,
        TokenType.VERIFY,
        timedelta(hours=settings.jwt_verify_token_expire_hours),
    )


def decode_token(token: str, expected_type: TokenType) -> str | None:
    """Decodifica e valida um JWT, retornando o `sub` ou `None` se inválido."""
    try:
        payload = jwt.decode(
            token,
            get_settings().jwt_secret_key,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        return None

    if payload.get("type") != expected_type.value:
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None
