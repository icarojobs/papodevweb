"""Migrations do MongoDB.

Em bancos de documentos a "migration" equivale à criação/garantia de índices
e restrições. Estas operações são idempotentes (podem rodar a cada inicialização).
"""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import (
    CONVERSATIONS_COLLECTION,
    MESSAGES_COLLECTION,
    USERS_COLLECTION,
)


async def run_migrations(database: AsyncIOMotorDatabase) -> None:
    """Aplica todas as migrations (índices) necessárias."""
    await database[USERS_COLLECTION].create_index("email", unique=True)
    # Busca de usuários por nome e listagem de conversas por participante.
    await database[USERS_COLLECTION].create_index("full_name")
    await database[CONVERSATIONS_COLLECTION].create_index("participants.user_id")
    await database[CONVERSATIONS_COLLECTION].create_index("updated_at")
    # Histórico de mensagens paginado por conversa.
    await database[MESSAGES_COLLECTION].create_index([("conversation_id", 1), ("created_at", -1)])
