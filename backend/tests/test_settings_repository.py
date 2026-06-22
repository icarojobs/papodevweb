"""Testes do repositório de configurações (singleton por chave)."""

import pytest

from app.repositories.settings_repository import SettingsRepository


@pytest.fixture
def settings_repository(mongo_database) -> SettingsRepository:
    return SettingsRepository(mongo_database)


async def test_get_missing_returns_none(settings_repository):
    assert await settings_repository.get("email") is None


async def test_upsert_then_get(settings_repository):
    await settings_repository.upsert("email", {"host": "smtp.x", "port": 587})
    document = await settings_repository.get("email")
    assert document["host"] == "smtp.x"
    assert document["port"] == 587


async def test_upsert_merges_fields(settings_repository):
    await settings_repository.upsert("email", {"host": "smtp.x", "port": 587})
    await settings_repository.upsert("email", {"port": 2525})
    document = await settings_repository.get("email")
    assert document["host"] == "smtp.x"  # mantido
    assert document["port"] == 2525  # atualizado
