"""Testes do serviço de e-mail (mockando o transporte SMTP)."""

from app.api.deps import get_email_sender, get_verification_email_sender
from app.core.config import Settings, get_settings
from app.services import email_service


def test_get_email_sender_returns_real_sender():
    assert get_email_sender() is email_service.send_password_reset_email


def test_get_verification_email_sender_returns_real_sender():
    assert get_verification_email_sender() is email_service.send_email_verification_email


async def test_send_email_verification_email(monkeypatch):
    captured = {}

    async def fake_send(message, hostname, port):
        captured["message"] = message

    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)

    await email_service.send_email_verification_email(
        "novo@example.com", "http://localhost:5173/confirmar-email?token=xyz"
    )

    assert captured["message"]["To"] == "novo@example.com"
    assert "xyz" in captured["message"].get_body(("plain",)).get_content()


async def test_send_password_reset_email(monkeypatch):
    captured = {}

    async def fake_send(message, hostname, port):
        captured["message"] = message
        captured["hostname"] = hostname
        captured["port"] = port

    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)

    await email_service.send_password_reset_email(
        "destino@example.com", "http://localhost:5173/redefinir-senha?token=abc123"
    )

    settings = get_settings()
    assert captured["hostname"] == settings.smtp_host
    assert captured["port"] == settings.smtp_port
    assert captured["message"]["To"] == "destino@example.com"
    assert "abc123" in captured["message"].get_body(("plain",)).get_content()


async def test_send_email_without_auth_omits_credentials(monkeypatch):
    """Mailpit (dev): sem usuário/senha e sem STARTTLS."""
    captured = {}

    async def fake_send(message, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)

    await email_service.send_password_reset_email("dev@example.com", "http://localhost/x?token=t")

    assert "username" not in captured
    assert "password" not in captured
    assert "start_tls" not in captured


async def test_send_email_uses_auth_and_tls_when_configured(monkeypatch):
    """Produção: STARTTLS + usuário/senha são repassados ao transporte."""
    captured = {}

    async def fake_send(message, **kwargs):
        captured.update(kwargs)

    custom = Settings(
        smtp_host="smtp.provedor.com",
        smtp_port=587,
        smtp_user="apikey",
        smtp_password="segredo",
        smtp_use_tls=True,
    )
    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)
    monkeypatch.setattr(email_service, "get_settings", lambda: custom)

    await email_service.send_email_verification_email(
        "prod@example.com", "https://papodevweb.com.br/confirmar-email?token=t"
    )

    assert captured["hostname"] == "smtp.provedor.com"
    assert captured["port"] == 587
    assert captured["username"] == "apikey"
    assert captured["password"] == "segredo"
    assert captured["start_tls"] is True
