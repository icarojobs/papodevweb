"""Ciclo de vida da conexão com o MongoDB (Motor / asyncio)."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


class MongoManager:
    """Encapsula o cliente Motor para um único ponto de acesso ao banco."""

    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None


mongo = MongoManager()


async def connect_to_mongo() -> None:
    """Abre a conexão com o MongoDB."""
    settings = get_settings()
    mongo.client = AsyncIOMotorClient(settings.mongodb_uri)
    mongo.database = mongo.client[settings.mongo_db_name]


async def close_mongo_connection() -> None:
    """Fecha a conexão com o MongoDB."""
    if mongo.client is not None:
        mongo.client.close()
        mongo.client = None
        mongo.database = None


def get_database() -> AsyncIOMotorDatabase:
    """Retorna a instância do banco de dados conectado."""
    if mongo.database is None:
        raise RuntimeError("Conexão com o MongoDB não inicializada.")
    return mongo.database
