"""Testes do ciclo de vida da conexão MongoDB e das dependências de banco."""

import pytest
from mongomock_motor import AsyncMongoMockClient

from app.api.deps import get_db
from app.db import mongodb


@pytest.fixture(autouse=True)
def reset_mongo_manager():
    """Garante estado limpo do singleton de conexão antes/depois de cada teste."""
    mongodb.mongo.client = None
    mongodb.mongo.database = None
    yield
    mongodb.mongo.client = None
    mongodb.mongo.database = None


def test_get_database_raises_when_not_connected():
    with pytest.raises(RuntimeError):
        mongodb.get_database()


async def test_connect_and_close_lifecycle(monkeypatch):
    monkeypatch.setattr(mongodb, "AsyncIOMotorClient", AsyncMongoMockClient)

    await mongodb.connect_to_mongo()
    assert mongodb.mongo.database is not None
    # get_db (dependência) e get_database devem retornar o banco conectado.
    assert get_db() is mongodb.get_database()

    await mongodb.close_mongo_connection()
    assert mongodb.mongo.client is None
    assert mongodb.mongo.database is None


async def test_close_without_connection_is_safe():
    await mongodb.close_mongo_connection()
    assert mongodb.mongo.client is None
