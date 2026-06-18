"""Modelo de domínio de mensagem e conversões para/from documento Mongo."""

from datetime import UTC, datetime
from typing import Any

from app.core.constants import MessageStatus, MessageType


class MediaInfo:
    """Metadados de uma mídia anexada a uma mensagem (imagem, arquivo, áudio)."""

    def __init__(
        self,
        *,
        key: str,
        url: str,
        mime: str,
        size: int,
        name: str,
        duration: float | None = None,
    ) -> None:
        self.key = key
        self.url = url
        self.mime = mime
        self.size = size
        self.name = name
        self.duration = duration

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "MediaInfo":
        return cls(
            key=document["key"],
            url=document["url"],
            mime=document["mime"],
            size=document["size"],
            name=document["name"],
            duration=document.get("duration"),
        )

    def to_document(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "url": self.url,
            "mime": self.mime,
            "size": self.size,
            "name": self.name,
            "duration": self.duration,
        }


class Message:
    """Entidade de domínio de uma mensagem."""

    def __init__(
        self,
        *,
        id: str,
        conversation_id: str,
        sender_id: str,
        type: MessageType,
        created_at: datetime,
        text: str = "",
        media: MediaInfo | None = None,
        delivered_to: list[str] | None = None,
        read_by: list[str] | None = None,
        deleted_for: list[str] | None = None,
        deleted_for_everyone: bool = False,
    ) -> None:
        self.id = id
        self.conversation_id = conversation_id
        self.sender_id = sender_id
        self.type = type
        self.created_at = created_at
        self.text = text
        self.media = media
        self.delivered_to = delivered_to or []
        self.read_by = read_by or []
        # Usuários que apagaram a mensagem "só para si".
        self.deleted_for = deleted_for or []
        # Apagada para todos (vira um aviso/tombstone).
        self.deleted_for_everyone = deleted_for_everyone

    def status_for(self, recipient_ids: list[str]) -> MessageStatus:
        """Calcula o status (enviado/entregue/lido) sob a ótica de quem enviou.

        Lido quando todos os destinatários leram; entregue quando todos
        receberam; caso contrário, apenas enviado.
        """
        if not recipient_ids:
            return MessageStatus.SENT
        if all(rid in self.read_by for rid in recipient_ids):
            return MessageStatus.READ
        if all(rid in self.delivered_to for rid in recipient_ids):
            return MessageStatus.DELIVERED
        return MessageStatus.SENT

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "Message":
        media = document.get("media")
        return cls(
            id=str(document["_id"]),
            conversation_id=str(document["conversation_id"]),
            sender_id=str(document["sender_id"]),
            type=MessageType(document["type"]),
            created_at=document["created_at"],
            text=document.get("text", ""),
            media=MediaInfo.from_document(media) if media else None,
            delivered_to=[str(uid) for uid in document.get("delivered_to", [])],
            read_by=[str(uid) for uid in document.get("read_by", [])],
            deleted_for=[str(uid) for uid in document.get("deleted_for", [])],
            deleted_for_everyone=document.get("deleted_for_everyone", False),
        )

    @staticmethod
    def new_document(
        *,
        conversation_id: str,
        sender_id: str,
        type: MessageType,
        text: str = "",
        media: MediaInfo | None = None,
    ) -> dict[str, Any]:
        """Monta o documento de uma nova mensagem pronto para inserção.

        O remetente já consta como tendo recebido e lido a própria mensagem.
        """
        return {
            "conversation_id": conversation_id,
            "sender_id": sender_id,
            "type": type.value,
            "text": text,
            "media": media.to_document() if media else None,
            "delivered_to": [sender_id],
            "read_by": [sender_id],
            "deleted_for": [],
            "deleted_for_everyone": False,
            "created_at": datetime.now(UTC),
        }
