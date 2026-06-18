"""Orquestração dos eventos de chat em tempo real (independente do transporte).

Toda a lógica de broadcast vive aqui, recebendo ``sio``, ``ChatService`` e
``PresenceService`` por injeção — o que mantém ``socket.py`` mínimo e permite
testar os fluxos com fakes (SOLID: Inversão de Dependência).
"""

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from app.core.constants import (
    ROOM_CONVERSATION_PREFIX,
    ROOM_USER_PREFIX,
    DeleteScope,
    MessageStatus,
    SocketEvent,
)
from app.models.conversation import Conversation
from app.schemas.chat import SendMessageRequest
from app.services.chat_service import ChatService
from app.services.exceptions import DomainError
from app.services.presence_service import PresenceService

MediaPurge = Callable[[list[str]], Awaitable[None]]


async def _noop_purge(_keys: list[str]) -> None:
    """Purga de mídia padrão (no-op) quando nenhuma é injetada."""


def _user_room(user_id: str) -> str:
    return f"{ROOM_USER_PREFIX}{user_id}"


def _conversation_room(conversation_id: str) -> str:
    return f"{ROOM_CONVERSATION_PREFIX}{conversation_id}"


class ChatRealtime:
    """Aplica regras de chat e emite os eventos correspondentes via Socket.IO."""

    def __init__(
        self,
        sio: Any,
        *,
        chat_service: ChatService,
        presence_service: PresenceService,
        media_purge: MediaPurge | None = None,
    ) -> None:
        self._sio = sio
        self._chat = chat_service
        self._presence = presence_service
        self._media_purge = media_purge or _noop_purge

    # ----- Conexão / presença -----

    async def on_connect(self, user_id: str) -> None:
        """Marca o usuário online, entrega pendências e avisa os contatos."""
        await self._presence.set_online(user_id)
        conversations = await self._chat.list_conversations(user_id)
        contacts: set[str] = set()
        for conversation in conversations:
            await self._deliver_pending(conversation.id, user_id)
            contacts.update(p.id for p in conversation.participants if p.id != user_id)
        await self._broadcast_presence(user_id, online=True, recipients=contacts)

    async def on_disconnect(self, user_id: str) -> None:
        """Marca o usuário offline (com visto por último) e avisa os contatos."""
        await self._presence.set_offline(user_id, now=datetime.now(UTC))
        contacts = await self._contacts_of(user_id)
        await self._broadcast_presence(user_id, online=False, recipients=contacts)

    # ----- Conversa aberta / leitura -----

    async def on_open(self, sid: str, user_id: str, conversation_id: str) -> None:
        """Usuário abriu uma conversa: entra na sala e marca como lida."""
        await self._sio.enter_room(sid, _conversation_room(conversation_id))
        await self.on_read(user_id, conversation_id)

    async def on_read(self, user_id: str, conversation_id: str) -> None:
        """Marca mensagens como lidas e emite os recibos de leitura."""
        try:
            result = await self._chat.mark_read(conversation_id, user_id)
        except DomainError:
            return
        if result.message_ids:
            await self._broadcast_status(
                result.conversation, result.message_ids, MessageStatus.READ, user_id
            )
        await self._emit_conversation_updated(result.conversation)

    # ----- Envio de mensagem -----

    async def on_send(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Persiste e propaga uma nova mensagem. Retorna o ack ao remetente."""
        try:
            request = SendMessageRequest(**payload)
            result = await self._chat.send_message(
                request.conversation_id,
                user_id,
                type=request.type,
                text=request.text,
                media=request.media,
            )
        except (DomainError, ValueError, TypeError) as exc:
            return {"ok": False, "error": str(exc)}

        message_public = self._chat.to_public_message(result.message, result.conversation)
        payload_out = {
            "conversation_id": result.conversation.id,
            "message": message_public.model_dump(mode="json"),
        }
        await self._emit_to_participants(
            result.conversation, SocketEvent.MESSAGE_NEW, payload_out
        )
        await self._emit_conversation_updated(result.conversation)
        return {"ok": True, "message": message_public.model_dump(mode="json")}

    async def on_delete_message(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Apaga uma mensagem (para mim/para todos) e propaga o tombstone."""
        try:
            conversation_id = payload["conversation_id"]
            message_id = payload["message_id"]
            scope = DeleteScope(payload.get("scope", DeleteScope.ME.value))
            result = await self._chat.delete_message(
                conversation_id, message_id, user_id, scope=scope
            )
        except (DomainError, ValueError, KeyError, TypeError) as exc:
            return {"ok": False, "error": str(exc)}

        await self._media_purge(result.media_keys)
        data = {
            "conversation_id": result.conversation_id,
            "message_id": result.message_id,
            "scope": result.scope.value,
        }
        for recipient_id in result.notify_ids:
            await self._sio.emit(SocketEvent.MESSAGE_DELETED, data, room=_user_room(recipient_id))
        if result.scope is DeleteScope.EVERYONE:
            await self._emit_conversation_updated(result.conversation)
        return {"ok": True}

    # ----- Digitação -----

    async def on_typing(self, user_id: str, conversation_id: str, typing: bool) -> None:
        """Avisa os demais participantes que o usuário está (ou não) digitando."""
        try:
            conversation = await self._chat.get_conversation(conversation_id, user_id)
        except DomainError:
            return
        data = {"conversation_id": conversation_id, "user_id": user_id, "typing": typing}
        for participant in conversation.participants:
            if participant.id != user_id:
                await self._sio.emit(
                    SocketEvent.TYPING, data, room=_user_room(participant.id)
                )

    # ----- Helpers de broadcast -----

    async def _deliver_pending(self, conversation_id: str, user_id: str) -> None:
        message_ids = await self._chat.mark_delivered(conversation_id, user_id)
        if not message_ids:
            return
        conversation = await self._chat.get_conversation(conversation_id, user_id)
        await self._broadcast_status(
            conversation, message_ids, MessageStatus.DELIVERED, user_id
        )

    async def _broadcast_status(
        self,
        conversation: Any,
        message_ids: list[str],
        status: MessageStatus,
        actor_id: str,
    ) -> None:
        data = {
            "conversation_id": conversation.id,
            "message_ids": message_ids,
            "status": status.value,
            "user_id": actor_id,
        }
        await self._emit_to_participants(conversation, SocketEvent.MESSAGE_STATUS, data)

    async def _emit_conversation_updated(self, conversation: Conversation) -> None:
        """Emite a conversa atualizada para cada participante (visão própria)."""
        users_by_id, presence = await self._chat.hydration_context([conversation])
        for participant in conversation.participants:
            public = self._chat.build_conversation_public(
                conversation, participant.user_id, users_by_id=users_by_id, presence=presence
            )
            await self._sio.emit(
                SocketEvent.CONVERSATION_UPDATED,
                {"conversation": public.model_dump(mode="json")},
                room=_user_room(participant.user_id),
            )

    async def _emit_to_participants(
        self, conversation: Any, event: SocketEvent, data: dict[str, Any]
    ) -> None:
        for participant_id in self._participant_ids(conversation):
            await self._sio.emit(event, data, room=_user_room(participant_id))

    async def _broadcast_presence(
        self, user_id: str, *, online: bool, recipients: set[str]
    ) -> None:
        last_seen = None if online else await self._presence.last_seen(user_id)
        data = {
            "user_id": user_id,
            "online": online,
            "last_seen": last_seen.isoformat() if last_seen else None,
        }
        for recipient_id in recipients:
            await self._sio.emit(SocketEvent.PRESENCE, data, room=_user_room(recipient_id))

    async def _contacts_of(self, user_id: str) -> set[str]:
        conversations = await self._chat.list_conversations(user_id)
        return {
            participant.id
            for conversation in conversations
            for participant in conversation.participants
            if participant.id != user_id
        }

    @staticmethod
    def _participant_ids(conversation: Any) -> list[str]:
        """Suporta tanto a entidade de domínio quanto o DTO público."""
        if isinstance(conversation, Conversation):
            return conversation.participant_ids
        return [participant.id for participant in conversation.participants]
