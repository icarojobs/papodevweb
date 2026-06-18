"""Repositório de conversas — acesso à coleção de conversas do MongoDB."""

from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import CONVERSATIONS_COLLECTION, ConversationType
from app.models.conversation import Conversation
from app.repositories.object_id import to_object_id

_DIRECT_PARTICIPANTS = 2


class ConversationRepository:
    """Abstrai o acesso à coleção de conversas (padrão Repository)."""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database[CONVERSATIONS_COLLECTION]

    async def create(self, document: dict[str, Any]) -> Conversation:
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return Conversation.from_document(document)

    async def get_by_id(self, conversation_id: str) -> Conversation | None:
        object_id = to_object_id(conversation_id)
        if object_id is None:
            return None
        document = await self._collection.find_one({"_id": object_id})
        return Conversation.from_document(document) if document else None

    async def find_direct_between(self, user_a: str, user_b: str) -> Conversation | None:
        """Localiza a conversa direta entre dois usuários, se já existir."""
        wanted = {user_a, user_b}
        cursor = self._collection.find(
            {"type": ConversationType.DIRECT.value, "participants.user_id": user_a}
        )
        async for document in cursor:
            conversation = Conversation.from_document(document)
            if set(conversation.participant_ids) == wanted:
                return conversation
        return None

    async def list_for_user(self, user_id: str) -> list[Conversation]:
        """Lista as conversas visíveis do usuário, da mais recente à mais antiga.

        Conversas excluídas "só para mim" (``deleted_for``) ficam ocultas.
        """
        cursor = self._collection.find(
            {"participants.user_id": user_id, "deleted_for": {"$ne": user_id}}
        ).sort("updated_at", -1)
        return [Conversation.from_document(document) async for document in cursor]

    async def bump_after_message(
        self,
        conversation: Conversation,
        *,
        last_message: dict[str, Any],
        sender_id: str,
        now: datetime,
    ) -> None:
        """Atualiza a prévia e incrementa o não-lido dos demais participantes."""
        participants = []
        for participant in conversation.participants:
            document = participant.to_document()
            if participant.user_id != sender_id:
                document["unread"] = participant.unread + 1
            participants.append(document)
        # Nova atividade faz a conversa reaparecer para quem a havia excluído.
        await self._update(
            conversation.id,
            {
                "last_message": last_message,
                "updated_at": now,
                "participants": participants,
                "deleted_for": [],
            },
        )

    async def reset_unread(self, conversation_id: str, user_id: str, *, now: datetime) -> bool:
        """Zera o contador de não-lidos de um participante. Retorna sucesso."""
        conversation = await self.get_by_id(conversation_id)
        if conversation is None or conversation.participant(user_id) is None:
            return False
        participants = []
        for participant in conversation.participants:
            document = participant.to_document()
            if participant.user_id == user_id:
                document["unread"] = 0
                document["last_read_at"] = now
            participants.append(document)
        await self._update(conversation_id, {"participants": participants})
        return True

    async def set_favourite(self, conversation_id: str, user_id: str, favourite: bool) -> bool:
        """Define o estado de favorito de uma conversa para um participante."""
        conversation = await self.get_by_id(conversation_id)
        if conversation is None or conversation.participant(user_id) is None:
            return False
        participants = []
        for participant in conversation.participants:
            document = participant.to_document()
            if participant.user_id == user_id:
                document["favourite"] = favourite
            participants.append(document)
        await self._update(conversation_id, {"participants": participants})
        return True

    async def remove_participant(self, conversation_id: str, user_id: str) -> int:
        """Remove um participante. Retorna a quantidade de participantes restantes."""
        conversation = await self.get_by_id(conversation_id)
        if conversation is None:
            return 0
        remaining = [p.to_document() for p in conversation.participants if p.user_id != user_id]
        await self._update(conversation_id, {"participants": remaining})
        return len(remaining)

    async def mark_deleted_for(
        self, conversation_id: str, user_id: str, *, now: datetime
    ) -> int:
        """Oculta a conversa para um usuário (exclusão "só para mim").

        Retorna quantos participantes ainda NÃO a excluíram.
        """
        conversation = await self.get_by_id(conversation_id)
        if conversation is None:
            return 0
        participants = []
        for participant in conversation.participants:
            document = participant.to_document()
            if participant.user_id == user_id:
                document["unread"] = 0
                document["cleared_at"] = now
            participants.append(document)
        deleted_for = sorted({*conversation.deleted_for, user_id})
        await self._update(
            conversation_id, {"participants": participants, "deleted_for": deleted_for}
        )
        active = [pid for pid in conversation.participant_ids if pid not in deleted_for]
        return len(active)

    async def delete(self, conversation_id: str) -> None:
        """Remove definitivamente o documento da conversa."""
        object_id = to_object_id(conversation_id)
        if object_id is not None:
            await self._collection.delete_one({"_id": object_id})

    async def delete_stale_before(self, cutoff: datetime) -> int:
        """Remove conversas sem atividade desde o corte. Retorna a quantidade removida."""
        result = await self._collection.delete_many({"updated_at": {"$lt": cutoff}})
        return result.deleted_count

    async def update_last_message_text(self, conversation_id: str, text: str) -> None:
        """Atualiza o texto da prévia (ex.: tombstone de mensagem apagada)."""
        conversation = await self.get_by_id(conversation_id)
        if conversation is None or not conversation.last_message:
            return
        last_message = {**conversation.last_message, "text": text}
        await self._update(conversation_id, {"last_message": last_message})

    async def _update(self, conversation_id: str, fields: dict[str, Any]) -> None:
        object_id = to_object_id(conversation_id)
        if object_id is None:
            return
        await self._collection.update_one({"_id": object_id}, {"$set": fields})
