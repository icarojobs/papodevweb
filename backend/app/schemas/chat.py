"""Schemas (DTOs) de chat validados via Pydantic."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.core.constants import (
    MAX_GROUP_NAME_LENGTH,
    MAX_MESSAGE_LENGTH,
    MIN_GROUP_NAME_LENGTH,
    ConversationType,
    MessageStatus,
    MessageType,
)


class ChatUser(BaseModel):
    """Usuário exposto dentro do contexto de chat (com presença)."""

    id: str
    full_name: str
    email: str
    online: bool = False
    last_seen: datetime | None = None


class MediaPublic(BaseModel):
    """Metadados públicos de uma mídia anexada."""

    key: str
    url: str
    mime: str
    size: int
    name: str
    duration: float | None = None


class MessagePublic(BaseModel):
    """Representação pública de uma mensagem."""

    id: str
    conversation_id: str
    sender_id: str
    type: MessageType
    text: str = ""
    media: MediaPublic | None = None
    created_at: datetime
    status: MessageStatus = MessageStatus.SENT
    read_by: list[str] = Field(default_factory=list)
    delivered_to: list[str] = Field(default_factory=list)
    deleted: bool = False


class ConversationPublic(BaseModel):
    """Representação pública de uma conversa, relativa a quem visualiza."""

    id: str
    type: ConversationType
    name: str
    participants: list[ChatUser]
    last_message: MessagePublic | None = None
    unread: int = 0
    favourite: bool = False
    created_at: datetime
    updated_at: datetime


class CreateConversationRequest(BaseModel):
    """Cria uma conversa direta (recipient_id) ou em grupo (name + member_ids)."""

    type: ConversationType = ConversationType.DIRECT
    recipient_id: str | None = None
    name: str | None = Field(
        default=None, min_length=MIN_GROUP_NAME_LENGTH, max_length=MAX_GROUP_NAME_LENGTH
    )
    member_ids: list[str] = Field(default_factory=list)


class MediaPayload(BaseModel):
    """Payload de mídia recebido ao enviar uma mensagem com anexo."""

    key: str
    url: str
    mime: str
    size: int
    name: str
    duration: float | None = None


class SendMessageRequest(BaseModel):
    """Payload de envio de mensagem (via Socket.IO)."""

    conversation_id: str
    type: MessageType = MessageType.TEXT
    text: str = Field(default="", max_length=MAX_MESSAGE_LENGTH)
    media: MediaPayload | None = None


class FavouriteResponse(BaseModel):
    """Resposta da alternância de favorito de uma conversa."""

    favourite: bool


class UploadResponse(MediaPublic):
    """Resposta do upload de mídia (mesma forma de MediaPublic)."""
