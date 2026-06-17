"""Testes do serviço de e-mail (mockando o transporte SMTP)."""

from app.api.deps import get_email_sender, get_verification_email_sender
from app.core.config import get_settings
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
