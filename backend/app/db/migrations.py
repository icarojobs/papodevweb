"""Migrations do MongoDB.

Em bancos de documentos a "migration" equivale à criação/garantia de índices
e restrições. Estas operações são idempotentes (podem rodar a cada inicialização).
"""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import USERS_COLLECTION


async def run_migrations(database: AsyncIOMotorDatabase) -> None:
    """Aplica todas as migrations (índices) necessárias."""
    await database[USERS_COLLECTION].create_index("email", unique=True)
