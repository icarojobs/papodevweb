"""Seeders de dados iniciais.

Todos os seeders são idempotentes: rodar mais de uma vez não duplica registros.
"""

import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import (
    DEFAULT_USER_EMAIL,
    DEFAULT_USER_FULL_NAME,
    DEFAULT_USER_PASSWORD,
)
from app.core.security import hash_password
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


async def seed_default_user(database: AsyncIOMotorDatabase) -> bool:
    """Garante o usuário padrão de testes, sempre pré-confirmado (ativo).

    Retorna ``True`` se o usuário foi criado agora, ``False`` se já existia.
    Idempotente e auto-corretivo: se o usuário já existir porém inativo
    (ex.: criado por uma versão anterior do seed), ele é reativado.
    """
    repository = UserRepository(database)
    existing = await repository.get_by_email(DEFAULT_USER_EMAIL)
    if existing is not None:
        if not existing.is_active:
            await repository.activate_user(existing.id)
        return False

    await repository.create(
        full_name=DEFAULT_USER_FULL_NAME,
        email=DEFAULT_USER_EMAIL,
        hashed_password=hash_password(DEFAULT_USER_PASSWORD),
        is_active=True,  # usuário de desenvolvimento já nasce confirmado.
    )
    return True


async def run_seeders(database: AsyncIOMotorDatabase) -> None:
    """Executa todos os seeders da aplicação."""
    if await seed_default_user(database):
        logger.info("Seed: usuário padrão '%s' criado.", DEFAULT_USER_EMAIL)
    else:
        logger.info("Seed: usuário padrão '%s' já existe.", DEFAULT_USER_EMAIL)
