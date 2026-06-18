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
