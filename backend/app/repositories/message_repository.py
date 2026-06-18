"""Repositório de mensagens — acesso à coleção de mensagens do MongoDB."""

from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import DEFAULT_MESSAGE_PAGE_SIZE, MESSAGES_COLLECTION
from app.models.message import Message
from app.repositories.object_id import to_object_id


class MessageRepository:
    """Abstrai o acesso à coleção de mensagens (padrão Repository)."""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database[MESSAGES_COLLECTION]

    async def create(self, document: dict[str, Any]) -> Message:
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return Message.from_document(document)

    async def get_by_id(self, message_id: str) -> Message | None:
        object_id = to_object_id(message_id)
        if object_id is None:
            return None
        document = await self._collection.find_one({"_id": object_id})
        return Message.from_document(document) if document else None

    async def hide_for_user(self, message_id: str, user_id: str) -> bool:
        """Oculta uma mensagem para um usuário (apagar só para mim)."""
        object_id = to_object_id(message_id)
        if object_id is None:
            return False
        result = await self._collection.update_one(
            {"_id": object_id}, {"$addToSet": {"deleted_for": user_id}}
        )
        return result.matched_count == 1

    async def delete_for_everyone(self, message_id: str) -> str | None:
        """Transforma a mensagem em tombstone (apagada para todos).

        Limpa o conteúdo e retorna a chave de mídia a purgar (se houver).
        """
        message = await self.get_by_id(message_id)
        if message is None:
            return None
        media_key = message.media.key if message.media else None
        await self._collection.update_one(
            {"_id": to_object_id(message_id)},
            {"$set": {"deleted_for_everyone": True, "text": "", "media": None}},
        )
        return media_key

    async def list_for_conversation(
        self,
        conversation_id: str,
        *,
        before: datetime | None = None,
        after: datetime | None = None,
        viewer_id: str | None = None,
        limit: int = DEFAULT_MESSAGE_PAGE_SIZE,
    ) -> list[Message]:
        """Histórico de uma conversa em ordem cronológica (mais antiga -> recente).

        Pagina do mais recente para trás usando ``before`` como cursor; ``after``
        oculta mensagens anteriores ao marco de limpeza do usuário; ``viewer_id``
        oculta mensagens apagadas só para esse usuário. O resultado é reordenado
        de forma ascendente para exibição.
        """
        created_at: dict[str, Any] = {}
        if before is not None:
            created_at["$lt"] = before
        if after is not None:
            created_at["$gt"] = after
        filters: dict[str, Any] = {"conversation_id": conversation_id}
        if created_at:
            filters["created_at"] = created_at
        if viewer_id is not None:
            filters["deleted_for"] = {"$ne": viewer_id}
        cursor = self._collection.find(filters).sort("created_at", -1).limit(limit)
        messages = [Message.from_document(document) async for document in cursor]
        messages.reverse()
        return messages

    async def media_keys(
        self, conversation_id: str, *, sender_id: str | None = None
    ) -> list[str]:
        """Chaves de objeto (MinIO) das mídias da conversa, opcionalmente de um remetente."""
        filters: dict[str, Any] = {"conversation_id": conversation_id, "media": {"$ne": None}}
        if sender_id is not None:
            filters["sender_id"] = sender_id
        cursor = self._collection.find(filters, {"media.key": 1})
        return [document["media"]["key"] async for document in cursor if document.get("media")]

    async def delete_by_conversation(self, conversation_id: str) -> int:
        """Remove todas as mensagens de uma conversa. Retorna a quantidade removida."""
        result = await self._collection.delete_many({"conversation_id": conversation_id})
        return result.deleted_count

    async def media_keys_before(self, cutoff: datetime) -> list[str]:
        """Chaves de mídia das mensagens criadas antes do corte (para purga)."""
        cursor = self._collection.find(
            {"created_at": {"$lt": cutoff}, "media": {"$ne": None}}, {"media.key": 1}
        )
        return [document["media"]["key"] async for document in cursor if document.get("media")]

    async def delete_before(self, cutoff: datetime) -> int:
        """Remove mensagens criadas antes do corte. Retorna a quantidade removida."""
        result = await self._collection.delete_many({"created_at": {"$lt": cutoff}})
        return result.deleted_count

    async def _ids_pending(self, conversation_id: str, user_id: str, field: str) -> list[str]:
        cursor = self._collection.find(
            {"conversation_id": conversation_id, field: {"$ne": user_id}},
            {"_id": 1},
        )
        return [str(document["_id"]) async for document in cursor]

    async def mark_delivered(self, conversation_id: str, user_id: str) -> list[str]:
        """Marca como entregues ao usuário as mensagens pendentes. Retorna os ids."""
        ids = await self._ids_pending(conversation_id, user_id, "delivered_to")
        if ids:
            await self._collection.update_many(
                {"conversation_id": conversation_id, "delivered_to": {"$ne": user_id}},
                {"$addToSet": {"delivered_to": user_id}},
            )
        return ids

    async def mark_read(self, conversation_id: str, user_id: str) -> list[str]:
        """Marca como lidas pelo usuário as mensagens pendentes. Retorna os ids."""
        ids = await self._ids_pending(conversation_id, user_id, "read_by")
        if ids:
            await self._collection.update_many(
                {"conversation_id": conversation_id, "read_by": {"$ne": user_id}},
                {"$addToSet": {"read_by": user_id, "delivered_to": user_id}},
            )
        return ids
