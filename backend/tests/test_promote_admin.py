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


async def test_promote_activates_inactive_user(monkeypatch):
    repo = await _setup_db(monkeypatch)
    await repo.create(full_name="A", email="a@x.com", hashed_password="h", is_active=False)

    code = await promote_admin.promote("a@x.com", revoke=False)

    assert code == 0
    user = await repo.get_by_email("a@x.com")
    assert user.is_admin is True
    assert user.is_active is True


async def test_create_admin_when_missing_with_password(monkeypatch):
    repo = await _setup_db(monkeypatch)

    code = await promote_admin.promote(
        "novo@x.com", revoke=False, password="senhaForte123", name="Novo Admin"
    )

    assert code == 0
    user = await repo.get_by_email("novo@x.com")
    assert user is not None
    assert user.is_admin is True
    assert user.is_active is True
    assert user.full_name == "Novo Admin"


async def test_missing_user_without_password_returns_1(monkeypatch):
    await _setup_db(monkeypatch)
    code = await promote_admin.promote("missing@x.com", revoke=False)
    assert code == 1


async def test_revoke_admin(monkeypatch):
    repo = await _setup_db(monkeypatch)
    user = await repo.create(full_name="A", email="a@x.com", hashed_password="h", is_active=True)
    await repo.set_admin(user.id, is_admin=True)

    code = await promote_admin.promote("a@x.com", revoke=True)

    assert code == 0
    assert (await repo.get_by_email("a@x.com")).is_admin is False


async def test_revoke_missing_user_returns_1(monkeypatch):
    await _setup_db(monkeypatch)
    code = await promote_admin.promote("missing@x.com", revoke=True)
    assert code == 1
