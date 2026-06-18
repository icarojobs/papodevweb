"""Modelo de domínio de conversa (direta ou em grupo) e conversões Mongo."""

from datetime import UTC, datetime
from typing import Any

from app.core.constants import ConversationType


class Participant:
    """Metadados de um participante dentro de uma conversa (por usuário)."""

    def __init__(
        self,
        *,
        user_id: str,
        unread: int = 0,
        favourite: bool = False,
        last_read_at: datetime | None = None,
        cleared_at: datetime | None = None,
    ) -> None:
        self.user_id = user_id
        self.unread = unread
        self.favourite = favourite
        self.last_read_at = last_read_at
        # Marco de "limpeza" da conversa: ao excluir só para si, o usuário passa
        # a ver apenas mensagens posteriores a este instante.
        self.cleared_at = cleared_at

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "Participant":
        return cls(
            user_id=str(document["user_id"]),
            unread=document.get("unread", 0),
            favourite=document.get("favourite", False),
            last_read_at=document.get("last_read_at"),
            cleared_at=document.get("cleared_at"),
        )

    def to_document(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "unread": self.unread,
            "favourite": self.favourite,
            "last_read_at": self.last_read_at,
            "cleared_at": self.cleared_at,
        }


class Conversation:
    """Entidade de domínio de uma conversa."""

    def __init__(
        self,
        *,
        id: str,
        type: ConversationType,
        participants: list[Participant],
        created_by: str,
        created_at: datetime,
        updated_at: datetime,
        name: str | None = None,
        last_message: dict[str, Any] | None = None,
        deleted_for: list[str] | None = None,
    ) -> None:
        self.id = id
        self.type = type
        self.participants = participants
        self.created_by = created_by
        self.created_at = created_at
        self.updated_at = updated_at
        self.name = name
        self.last_message = last_message
        # Usuários que excluíram a conversa "só para si" (ocultada da lista).
        self.deleted_for = deleted_for or []

    @property
    def participant_ids(self) -> list[str]:
        return [participant.user_id for participant in self.participants]

    def participant(self, user_id: str) -> Participant | None:
        """Retorna os metadados de um participante específico, se existir."""
        return next((p for p in self.participants if p.user_id == user_id), None)

    def other_participant_ids(self, user_id: str) -> list[str]:
        """Ids dos demais participantes (exceto o informado)."""
        return [pid for pid in self.participant_ids if pid != user_id]

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "Conversation":
        return cls(
            id=str(document["_id"]),
            type=ConversationType(document["type"]),
            participants=[Participant.from_document(p) for p in document.get("participants", [])],
            created_by=str(document["created_by"]),
            created_at=document["created_at"],
            updated_at=document["updated_at"],
            name=document.get("name"),
            last_message=document.get("last_message"),
            deleted_for=[str(uid) for uid in document.get("deleted_for", [])],
        )

    @staticmethod
    def new_document(
        *,
        type: ConversationType,
        participant_ids: list[str],
        created_by: str,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Monta o documento de uma nova conversa pronto para inserção."""
        now = datetime.now(UTC)
        return {
            "type": type.value,
            "name": name,
            "created_by": created_by,
            "participants": [
                Participant(user_id=user_id).to_document() for user_id in participant_ids
            ],
            "last_message": None,
            "deleted_for": [],
            "created_at": now,
            "updated_at": now,
        }
