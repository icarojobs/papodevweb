"""Testes dos seeders de dados iniciais."""

from app.core.constants import DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD
from app.core.security import verify_password
from app.db.seed import run_seeders, seed_default_user
from app.repositories.user_repository import UserRepository


async def test_seed_creates_default_user(mongo_database):
    created = await seed_default_user(mongo_database)
    assert created is True

    user = await UserRepository(mongo_database).get_by_email(DEFAULT_USER_EMAIL)
    assert user is not None
    assert user.email == DEFAULT_USER_EMAIL
    assert user.is_active is True  # usuário de dev já nasce confirmado
    assert verify_password(DEFAULT_USER_PASSWORD, user.hashed_password) is True


async def test_seed_is_idempotent(mongo_database):
    assert await seed_default_user(mongo_database) is True
    assert await seed_default_user(mongo_database) is False


async def test_seed_reactivates_existing_inactive_default_user(mongo_database):
    repository = UserRepository(mongo_database)
    # Simula usuário padrão criado por versão anterior, sem ativação.
    user = await repository.create(
        full_name="Usuário Teste",
        email=DEFAULT_USER_EMAIL,
        hashed_password="hash",
        is_active=False,
    )

    created = await seed_default_user(mongo_database)

    assert created is False  # já existia
    refreshed = await repository.get_by_id(user.id)
    assert refreshed is not None
    assert refreshed.is_active is True  # foi reativado pelo seed


async def test_run_seeders_creates_then_skips(mongo_database):
    await run_seeders(mongo_database)  # cria (cobre o log de criação)
    await run_seeders(mongo_database)  # já existe (cobre o log de existência)

    assert await UserRepository(mongo_database).exists_by_email(DEFAULT_USER_EMAIL)
