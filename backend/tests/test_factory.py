"""Testes das fábricas de serviços e dos provedores de dependência."""

from app.api import deps
from app.db import mongodb
from app.services import factory
from app.services.chat_service import ChatService
from app.services.media_service import MediaService
from app.services.presence_service import PresenceService


def test_build_presence_service():
    assert isinstance(factory.build_presence_service(), PresenceService)


def test_build_media_service():
    assert isinstance(factory.build_media_service(), MediaService)


def test_get_redis_and_minio_are_cached():
    assert factory.get_redis() is factory.get_redis()
    assert factory.get_minio() is factory.get_minio()
    assert factory.get_minio_public() is factory.get_minio_public()
    # Cliente interno e público são instâncias distintas.
    assert factory.get_minio() is not factory.get_minio_public()


async def test_build_chat_service(mongo_database, monkeypatch):
    monkeypatch.setattr(mongodb.mongo, "database", mongo_database)
    assert isinstance(factory.build_chat_service(), ChatService)


def test_deps_presence_and_media_providers():
    assert isinstance(deps.get_presence_service(), PresenceService)
    assert isinstance(deps.get_media_service(), MediaService)


def test_minio_clients_use_independent_ssl(monkeypatch):
    """Interno usa minio_use_ssl; público usa minio_public_use_ssl (HTTPS em prod)."""
    from app.core.config import Settings

    calls: dict[str, bool] = {}

    class FakeMinio:
        def __init__(self, endpoint, **kwargs):
            calls[endpoint] = kwargs["secure"]

    custom = Settings(
        minio_endpoint="minio:9000",
        minio_public_endpoint="media.papodevweb.com.br",
        minio_use_ssl=False,
        minio_public_use_ssl=True,
    )
    monkeypatch.setattr(factory, "Minio", FakeMinio)
    monkeypatch.setattr(factory, "get_settings", lambda: custom)
    factory.get_minio.cache_clear()
    factory.get_minio_public.cache_clear()
    try:
        factory.get_minio()
        factory.get_minio_public()
        assert calls["minio:9000"] is False
        assert calls["media.papodevweb.com.br"] is True
    finally:
        factory.get_minio.cache_clear()
        factory.get_minio_public.cache_clear()
