"""Testes do serviço de e-mail (mockando o transporte SMTP e a config efetiva)."""

from mongomock_motor import AsyncMongoMockClient

from app.api.deps import (
    get_email_sender,
    get_test_email_sender,
    get_verification_email_sender,
)
from app.core.config import get_settings
from app.core.constants import TEST_EMAIL_SUBJECT
from app.services import email_service
from app.services.settings_service import EmailConfig


def _config(**overrides) -> EmailConfig:
    """Cria uma EmailConfig de teste com valores padrão sobreponíveis."""
    base = {
        "host": "smtp.local",
        "port": 1025,
        "username": "",
        "password": "",
        "from_email": "no-reply@papodevweb.local",
        "from_name": "Papo Dev Web",
        "use_tls": False,
    }
    base.update(overrides)
    return EmailConfig(**base)


def _patch_config(monkeypatch, config: EmailConfig) -> None:
    async def fake_effective_config() -> EmailConfig:
        return config

    monkeypatch.setattr(email_service, "_effective_config", fake_effective_config)


def test_get_email_sender_returns_real_sender():
    assert get_email_sender() is email_service.send_password_reset_email


def test_get_verification_email_sender_returns_real_sender():
    assert get_verification_email_sender() is email_service.send_email_verification_email


def test_get_test_email_sender_returns_real_sender():
    assert get_test_email_sender() is email_service.send_test_email


async def test_send_email_verification_email(monkeypatch):
    captured = {}

    async def fake_send(message, **kwargs):
        captured["message"] = message

    _patch_config(monkeypatch, _config())
    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)

    await email_service.send_email_verification_email(
        "novo@example.com", "http://localhost:5173/confirmar-email?token=xyz"
    )

    assert captured["message"]["To"] == "novo@example.com"
    assert "xyz" in captured["message"].get_body(("plain",)).get_content()


async def test_send_password_reset_email(monkeypatch):
    captured = {}

    async def fake_send(message, **kwargs):
        captured["message"] = message
        captured["kwargs"] = kwargs

    _patch_config(monkeypatch, _config(host="smtp.reset", port=2525))
    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)

    await email_service.send_password_reset_email(
        "destino@example.com", "http://localhost:5173/redefinir-senha?token=abc123"
    )

    assert captured["kwargs"]["hostname"] == "smtp.reset"
    assert captured["kwargs"]["port"] == 2525
    assert captured["message"]["To"] == "destino@example.com"
    assert "abc123" in captured["message"].get_body(("plain",)).get_content()


async def test_send_email_without_auth_omits_credentials(monkeypatch):
    """Mailpit (dev): sem usuário/senha e sem STARTTLS."""
    captured = {}

    async def fake_send(message, **kwargs):
        captured.update(kwargs)

    _patch_config(monkeypatch, _config(use_tls=False, username=""))
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

    _patch_config(
        monkeypatch,
        _config(
            host="smtp.provedor.com",
            port=587,
            username="apikey",
            password="segredo",
            use_tls=True,
        ),
    )
    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)

    await email_service.send_email_verification_email(
        "prod@example.com", "https://papodevweb.com.br/confirmar-email?token=t"
    )

    assert captured["hostname"] == "smtp.provedor.com"
    assert captured["port"] == 587
    assert captured["username"] == "apikey"
    assert captured["password"] == "segredo"
    assert captured["start_tls"] is True
    # STARTTLS (587) não deve usar TLS implícito.
    assert "use_tls" not in captured


async def test_send_email_uses_implicit_tls_on_port_465(monkeypatch):
    """Porta 465: TLS implícito (use_tls), nunca STARTTLS — senão trava no handshake."""
    captured = {}

    async def fake_send(message, **kwargs):
        captured.update(kwargs)

    _patch_config(
        monkeypatch,
        _config(
            host="smtp.provedor.com",
            port=465,
            username="apikey",
            password="segredo",
            use_tls=True,
        ),
    )
    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)

    await email_service.send_test_email("prod@example.com")

    assert captured["port"] == 465
    assert captured["use_tls"] is True
    assert "start_tls" not in captured


async def test_send_email_sets_timeout(monkeypatch):
    """O envio define um timeout para falhar rápido com host/porta/TLS errados."""
    from app.core.constants import SMTP_TIMEOUT_SECONDS

    captured = {}

    async def fake_send(message, **kwargs):
        captured.update(kwargs)

    _patch_config(monkeypatch, _config())
    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)

    await email_service.send_test_email("admin@example.com")

    assert captured["timeout"] == SMTP_TIMEOUT_SECONDS


async def test_send_test_email(monkeypatch):
    captured = {}

    async def fake_send(message, **kwargs):
        captured["message"] = message

    _patch_config(monkeypatch, _config())
    monkeypatch.setattr(email_service.aiosmtplib, "send", fake_send)

    await email_service.send_test_email("admin@example.com")

    assert captured["message"]["To"] == "admin@example.com"
    assert captured["message"]["Subject"] == TEST_EMAIL_SUBJECT


async def test_effective_config_falls_back_to_env(monkeypatch):
    """Sem configuração no banco, a config efetiva vem do .env."""
    client = AsyncMongoMockClient()
    monkeypatch.setattr(email_service, "get_database", lambda: client["papodevweb_test"])

    config = await email_service._effective_config()

    settings = get_settings()
    assert config.host == settings.smtp_host
    assert config.port == settings.smtp_port
