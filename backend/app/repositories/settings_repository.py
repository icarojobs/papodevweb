"""Repositório de configurações da plataforma (documentos singleton por chave)."""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import SETTINGS_COLLECTION


class SettingsRepository:
    """Acesso à coleção de configurações (um documento por chave, via _id)."""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database[SETTINGS_COLLECTION]

    async def get(self, key: str) -> dict[str, Any] | None:
        """Retorna o documento de configuração da chave, ou ``None``."""
        return await self._collection.find_one({"_id": key})

    async def upsert(self, key: str, values: dict[str, Any]) -> None:
        """Cria ou atualiza (merge) o documento de configuração da chave."""
        await self._collection.update_one({"_id": key}, {"$set": values}, upsert=True)
