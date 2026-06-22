"""Testes do serviço de configurações de e-mail de disparo."""

import pytest

from app.core.config import get_settings
from app.repositories.settings_repository import SettingsRepository
from app.schemas.settings import EmailSettingsUpdate
from app.services.settings_service import SettingsService


@pytest.fixture
def settings_service(mongo_database) -> SettingsService:
    return SettingsService(SettingsRepository(mongo_database))


def _update(**overrides) -> EmailSettingsUpdate:
    base = {
        "host": "smtp.provedor.com",
        "port": 587,
        "username": "apikey",
        "password": "segredo",
        "from_email": "no-reply@papodevweb.com.br",
        "from_name": "Papo Dev Web",
        "use_tls": True,
    }
    base.update(overrides)
    return EmailSettingsUpdate(**base)


async def test_get_email_settings_defaults_when_empty(settings_service):
    public = await settings_service.get_email_settings()
    assert public.host == ""
    assert public.password_set is False


async def test_update_encrypts_password_and_hides_it(settings_service):
    public = await settings_service.update_email_settings(_update())
    assert public.host == "smtp.provedor.com"
    assert public.username == "apikey"
    assert public.password_set is True
    # O schema público NÃO tem campo de senha (write-only).
    assert "password" not in public.model_dump()


async def test_update_without_password_keeps_existing(settings_service):
    await settings_service.update_email_settings(_update(password="segredo"))
    # Segunda atualização sem senha (None) deve manter a senha anterior.
    public = await settings_service.update_email_settings(_update(password=None, host="smtp.novo"))
    assert public.host == "smtp.novo"
    assert public.password_set is True
    config = await settings_service.get_effective_email_config()
    assert config.password == "segredo"


async def test_effective_config_prefers_db_and_decrypts(settings_service):
    await settings_service.update_email_settings(_update(host="smtp.db", password="topsecret"))
    config = await settings_service.get_effective_email_config()
    assert config.host == "smtp.db"
    assert config.username == "apikey"
    assert config.password == "topsecret"
    assert config.use_tls is True


async def test_effective_config_falls_back_to_env(settings_service):
    config = await settings_service.get_effective_email_config()
    settings = get_settings()
    assert config.host == settings.smtp_host
    assert config.from_email == settings.smtp_from
