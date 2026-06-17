"""Testes das migrations (índices) do MongoDB."""

from app.core.constants import USERS_COLLECTION
from app.db.migrations import run_migrations


async def test_run_migrations_creates_email_index(mongo_database):
    await run_migrations(mongo_database)
    indexes = await mongo_database[USERS_COLLECTION].index_information()
    assert any("email" in name for name in indexes)


async def test_run_migrations_is_idempotent(mongo_database):
    await run_migrations(mongo_database)
    await run_migrations(mongo_database)  # não deve lançar exceção
    indexes = await mongo_database[USERS_COLLECTION].index_information()
    assert any("email" in name for name in indexes)
