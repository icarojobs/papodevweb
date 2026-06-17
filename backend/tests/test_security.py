"""Testes das funções de segurança (hash e JWT)."""

from app.core.constants import TokenType
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_is_not_plaintext_and_verifies():
    hashed = hash_password("senhaSegura123")
    assert hashed != "senhaSegura123"
    assert verify_password("senhaSegura123", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("senhaSegura123")
    assert verify_password("senhaErrada", hashed) is False


def test_access_token_roundtrip():
    token = create_access_token("user-123")
    assert decode_token(token, TokenType.ACCESS) == "user-123"


def test_refresh_token_roundtrip():
    token = create_refresh_token("user-456")
    assert decode_token(token, TokenType.REFRESH) == "user-456"


def test_token_type_mismatch_returns_none():
    access = create_access_token("user-123")
    assert decode_token(access, TokenType.REFRESH) is None


def test_invalid_token_returns_none():
    assert decode_token("not-a-jwt", TokenType.ACCESS) is None


def test_password_reset_token_roundtrip():
    token = create_password_reset_token("user-789")
    assert decode_token(token, TokenType.RESET) == "user-789"


def test_reset_token_is_not_accepted_as_access():
    token = create_password_reset_token("user-789")
    assert decode_token(token, TokenType.ACCESS) is None
