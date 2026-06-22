"""Testes da criptografia simétrica de segredos (Fernet)."""

from app.core.crypto import decrypt_secret, encrypt_secret


def test_encrypt_decrypt_roundtrip():
    token = encrypt_secret("minha-senha-smtp")
    assert token != "minha-senha-smtp"  # de fato criptografado
    assert decrypt_secret(token) == "minha-senha-smtp"


def test_encrypt_is_non_deterministic():
    # Fernet inclui IV/timestamp: dois ciphertexts diferem para o mesmo texto.
    assert encrypt_secret("igual") != encrypt_secret("igual")


def test_decrypt_invalid_token_returns_none():
    assert decrypt_secret("isto-nao-e-um-token-fernet") is None
