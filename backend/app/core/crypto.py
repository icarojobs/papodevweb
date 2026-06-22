"""Criptografia simétrica (Fernet) para segredos em repouso (ex.: senha SMTP).

A chave do Fernet é derivada de ``settings_secret_key`` (ou ``jwt_secret_key``
como fallback) via SHA-256, evitando exigir uma chave em formato específico.
"""

import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


@lru_cache
def _fernet() -> Fernet:
    settings = get_settings()
    secret = settings.settings_secret_key or settings.jwt_secret_key
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return Fernet(key)


def encrypt_secret(plaintext: str) -> str:
    """Criptografa um texto puro, devolvendo o token Fernet (str)."""
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_secret(token: str) -> str | None:
    """Descriptografa um token Fernet; devolve ``None`` se inválido/corrompido."""
    try:
        return _fernet().decrypt(token.encode()).decode()
    except (InvalidToken, ValueError):
        return None
