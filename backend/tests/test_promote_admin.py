"""Testes do script de promoção/revogação de admin."""

from mongomock_motor import AsyncMongoMockClient

from app.repositories.user_repository import UserRepository
from scripts import promote_admin


async def _setup_db(monkeypatch):
    db = AsyncMongoMockClient()["papodevweb_test"]

    async def _noop() -> None:
        return None

    monkeypatch.setattr(promote_admin, "connect_to_mongo", _noop)
    monkeypatch.setattr(promote_admin, "close_mongo_connection", _noop)
    monkeypatch.setattr(promote_admin, "get_database", lambda: db)
    return UserRepository(db)


async def test_promote_sets_admin(monkeypatch):
    repo = await _setup_db(monkeypatch)
    await repo.create(full_name="A", email="a@x.com", hashed_password="h", is_active=True)

    code = await promote_admin.promote("a@x.com", revoke=False)

    assert code == 0
    assert (await repo.get_by_email("a@x.com")).is_admin is True


async def test_revoke_admin(monkeypatch):
    repo = await _setup_db(monkeypatch)
    user = await repo.create(full_name="A", email="a@x.com", hashed_password="h", is_active=True)
    await repo.set_admin(user.id, is_admin=True)

    code = await promote_admin.promote("a@x.com", revoke=True)

    assert code == 0
    assert (await repo.get_by_email("a@x.com")).is_admin is False


async def test_promote_user_not_found(monkeypatch):
    await _setup_db(monkeypatch)
    code = await promote_admin.promote("missing@x.com", revoke=False)
    assert code == 1
