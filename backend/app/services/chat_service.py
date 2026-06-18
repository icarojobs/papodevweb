"""Regras de negócio do chat: conversas, mensagens, recibos e favoritos."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.constants import (
    DEFAULT_MESSAGE_PAGE_SIZE,
    MAX_MESSAGE_PAGE_SIZE,
    MSG_MESSAGE_DELETED,
    ConversationType,
    DeleteScope,
    MessageType,
)
from app.models.conversation import Conversation
from app.models.message import MediaInfo, Message
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.schemas.chat import (
    ChatUser,
    ConversationPublic,
    CreateConversationRequest,
    MediaPayload,
    MediaPublic,
    MessagePublic,
)
from app.services.exceptions import (
    CannotDeleteForEveryoneError,
    CannotLeaveDirectError,
    ConversationNotFoundError,
    EmptyMessageError,
    GroupNeedsMembersError,
    MessageNotFoundError,
    NotAParticipantError,
    RecipientNotFoundError,
)
from app.services.presence_service import Presence, PresenceService

_PREVIEW_BY_TYPE = {
    MessageType.IMAGE: "📷 Foto",
    MessageType.VIDEO: "🎥 Vídeo",
    MessageType.DOCUMENT: "📄 Documento",
    MessageType.AUDIO: "🎤 Áudio",
}


@dataclass
class SendResult:
    """Resultado do envio: a mensagem criada e a conversa atualizada."""

    message: Message
    conversation: Conversation


@dataclass
class ReadResult:
    """Resultado da marcação de leitura: ids afetados e conversa."""

    message_ids: list[str]
    conversation: Conversation


@dataclass
class DeleteMessageResult:
    """Resultado da exclusão de uma mensagem (para mim ou para todos)."""

    scope: DeleteScope
    conversation_id: str
    message_id: str
    notify_ids: list[str]
    media_keys: list[str]
    conversation: Conversation


@dataclass
class DeleteResult:
    """Resultado de uma exclusão/saída: chaves de mídia a purgar e destinatários.

    ``media_keys`` lista os objetos a remover do armazenamento; ``notify_ids`` são
    os participantes que devem ter a conversa removida da sua visão.
    """

    media_keys: list[str]
    notify_ids: list[str]
    hard_deleted: bool


class ChatService:
    """Orquestra conversas e mensagens sobre os repositórios e a presença."""

    def __init__(
        self,
        *,
        conversations: ConversationRepository,
        messages: MessageRepository,
        users: UserRepository,
        presence: PresenceService,
        presign: Callable[[str], str] | None = None,
    ) -> None:
        self._conversations = conversations
        self._messages = messages
        self._users = users
        self._presence = presence
        # Resolve a URL de leitura de uma mídia a partir da sua chave. Quando
        # ausente, usa a URL gravada na mensagem (compatibilidade).
        self._presign = presign

    # ----- Usuários -----

    async def search_users(self, query: str, *, requester_id: str) -> list[ChatUser]:
        users = await self._users.search(query, exclude_id=requester_id)
        presence = await self._presence.presence_for([user.id for user in users])
        return [self._to_chat_user(user, presence) for user in users]

    # ----- Conversas -----

    async def list_conversations(self, user_id: str) -> list[ConversationPublic]:
        conversations = await self._conversations.list_for_user(user_id)
        users_by_id, presence = await self._hydration_context(conversations)
        return [
            self._to_public_conversation(conversation, user_id, users_by_id, presence)
            for conversation in conversations
        ]

    async def get_conversation(self, conversation_id: str, user_id: str) -> ConversationPublic:
        conversation = await self._require_participant(conversation_id, user_id)
        users_by_id, presence = await self._hydration_context([conversation])
        return self._to_public_conversation(conversation, user_id, users_by_id, presence)

    async def create_conversation(
        self, user_id: str, request: CreateConversationRequest
    ) -> ConversationPublic:
        if request.type is ConversationType.GROUP:
            conversation = await self._create_group(user_id, request)
        else:
            conversation = await self._get_or_create_direct(user_id, request.recipient_id)
        users_by_id, presence = await self._hydration_context([conversation])
        return self._to_public_conversation(conversation, user_id, users_by_id, presence)

    async def _get_or_create_direct(
        self, user_id: str, recipient_id: str | None
    ) -> Conversation:
        if not recipient_id or recipient_id == user_id:
            raise RecipientNotFoundError
        recipient = await self._users.get_by_id(recipient_id)
        if recipient is None:
            raise RecipientNotFoundError
        existing = await self._conversations.find_direct_between(user_id, recipient_id)
        if existing is not None:
            return existing
        document = Conversation.new_document(
            type=ConversationType.DIRECT,
            participant_ids=[user_id, recipient_id],
            created_by=user_id,
        )
        return await self._conversations.create(document)

    async def _create_group(
        self, user_id: str, request: CreateConversationRequest
    ) -> Conversation:
        members = await self._users.get_by_ids(request.member_ids)
        member_ids = {member.id for member in members if member.id != user_id}
        if not member_ids:
            raise GroupNeedsMembersError
        document = Conversation.new_document(
            type=ConversationType.GROUP,
            participant_ids=[user_id, *member_ids],
            created_by=user_id,
            name=(request.name or "").strip() or "Novo grupo",
        )
        return await self._conversations.create(document)

    async def toggle_favourite(self, conversation_id: str, user_id: str) -> bool:
        conversation = await self._require_participant(conversation_id, user_id)
        participant = conversation.participant(user_id)
        new_value = not (participant.favourite if participant else False)
        await self._conversations.set_favourite(conversation_id, user_id, new_value)
        return new_value

    async def leave_group(self, conversation_id: str, user_id: str) -> DeleteResult:
        """Remove o usuário de um grupo. Se ficar vazio, apaga o grupo e a mídia.

        Idempotente: se a conversa não existe mais, é um no-op bem-sucedido.
        """
        conversation = await self._conversation_for_removal(conversation_id, user_id)
        if conversation is None:
            return _noop_delete(user_id)
        if conversation.type is not ConversationType.GROUP:
            raise CannotLeaveDirectError
        remaining_ids = conversation.other_participant_ids(user_id)
        remaining = await self._conversations.remove_participant(conversation_id, user_id)
        if remaining == 0:
            return await self._purge(conversation_id, delete_media=True, notify_ids=[user_id])
        return DeleteResult(media_keys=[], notify_ids=remaining_ids, hard_deleted=False)

    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: str,
        *,
        scope: DeleteScope,
        delete_media: bool,
    ) -> DeleteResult:
        """Exclui a conversa só para o usuário ou para todos, purgando mídia se pedido.

        Idempotente: excluir uma conversa inexistente é um no-op bem-sucedido.
        """
        conversation = await self._conversation_for_removal(conversation_id, user_id)
        if conversation is None:
            return _noop_delete(user_id)
        if scope is DeleteScope.EVERYONE:
            notify_ids = conversation.participant_ids
            return await self._purge(
                conversation_id, delete_media=delete_media, notify_ids=notify_ids
            )

        # Escopo "só para mim": oculta a conversa e, opcionalmente, apaga as
        # mídias enviadas pelo próprio usuário.
        media_keys = (
            await self._messages.media_keys(conversation_id, sender_id=user_id)
            if delete_media
            else []
        )
        remaining_active = await self._conversations.mark_deleted_for(
            conversation_id, user_id, now=datetime.now(UTC)
        )
        if remaining_active == 0:
            # Ninguém mais enxerga a conversa: remove tudo definitivamente.
            purge = await self._purge(conversation_id, delete_media=True, notify_ids=[user_id])
            return DeleteResult(
                media_keys=sorted({*media_keys, *purge.media_keys}),
                notify_ids=[user_id],
                hard_deleted=True,
            )
        return DeleteResult(media_keys=media_keys, notify_ids=[user_id], hard_deleted=False)

    async def _purge(
        self, conversation_id: str, *, delete_media: bool, notify_ids: list[str]
    ) -> DeleteResult:
        """Apaga conversa e mensagens; coleta as chaves de mídia se solicitado."""
        media_keys = await self._messages.media_keys(conversation_id) if delete_media else []
        await self._messages.delete_by_conversation(conversation_id)
        await self._conversations.delete(conversation_id)
        return DeleteResult(media_keys=media_keys, notify_ids=notify_ids, hard_deleted=True)

    # ----- Mensagens -----

    async def get_messages(
        self,
        conversation_id: str,
        user_id: str,
        *,
        before: datetime | None = None,
        limit: int = DEFAULT_MESSAGE_PAGE_SIZE,
    ) -> list[MessagePublic]:
        conversation = await self._require_participant(conversation_id, user_id)
        page_size = max(1, min(limit, MAX_MESSAGE_PAGE_SIZE))
        participant = conversation.participant(user_id)
        cleared_at = participant.cleared_at if participant else None
        messages = await self._messages.list_for_conversation(
            conversation_id,
            before=before,
            after=cleared_at,
            viewer_id=user_id,
            limit=page_size,
        )
        return [self._to_public_message(message, conversation) for message in messages]

    async def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        *,
        type: MessageType = MessageType.TEXT,
        text: str = "",
        media: MediaPayload | None = None,
    ) -> SendResult:
        conversation = await self._require_participant(conversation_id, sender_id)
        clean_text = text.strip()
        if not clean_text and media is None:
            raise EmptyMessageError

        media_info = _media_info_from_payload(media)
        document = Message.new_document(
            conversation_id=conversation_id,
            sender_id=sender_id,
            type=type,
            text=clean_text,
            media=media_info,
        )
        message = await self._messages.create(document)

        now = datetime.now(UTC)
        await self._conversations.bump_after_message(
            conversation,
            last_message=_preview_of(message),
            sender_id=sender_id,
            now=now,
        )
        refreshed = await self._conversations.get_by_id(conversation_id)
        return SendResult(message=message, conversation=refreshed or conversation)

    async def mark_read(self, conversation_id: str, user_id: str) -> ReadResult:
        conversation = await self._require_participant(conversation_id, user_id)
        message_ids = await self._messages.mark_read(conversation_id, user_id)
        await self._conversations.reset_unread(conversation_id, user_id, now=datetime.now(UTC))
        refreshed = await self._conversations.get_by_id(conversation_id)
        return ReadResult(message_ids=message_ids, conversation=refreshed or conversation)

    async def mark_delivered(self, conversation_id: str, user_id: str) -> list[str]:
        await self._require_participant(conversation_id, user_id)
        return await self._messages.mark_delivered(conversation_id, user_id)

    async def delete_message(
        self, conversation_id: str, message_id: str, user_id: str, *, scope: DeleteScope
    ) -> DeleteMessageResult:
        """Apaga uma mensagem só para o usuário ou para todos (apenas o autor)."""
        conversation = await self._require_participant(conversation_id, user_id)
        message = await self._messages.get_by_id(message_id)
        if message is None or message.conversation_id != conversation_id:
            raise MessageNotFoundError

        if scope is DeleteScope.ME:
            await self._messages.hide_for_user(message_id, user_id)
            return DeleteMessageResult(
                scope=scope,
                conversation_id=conversation_id,
                message_id=message_id,
                notify_ids=[user_id],
                media_keys=[],
                conversation=conversation,
            )

        # Apagar para todos: somente o autor pode.
        if message.sender_id != user_id:
            raise CannotDeleteForEveryoneError
        media_key = await self._messages.delete_for_everyone(message_id)
        # Atualiza a prévia da conversa se a mensagem apagada era a última.
        updated = conversation
        if conversation.last_message and conversation.last_message.get("id") == message_id:
            await self._conversations.update_last_message_text(
                conversation_id, MSG_MESSAGE_DELETED
            )
            updated = await self._conversations.get_by_id(conversation_id) or conversation
        return DeleteMessageResult(
            scope=scope,
            conversation_id=conversation_id,
            message_id=message_id,
            notify_ids=conversation.participant_ids,
            media_keys=[media_key] if media_key else [],
            conversation=updated,
        )

    def build_conversation_public(
        self,
        conversation: Conversation,
        viewer_id: str,
        *,
        users_by_id: dict[str, User],
        presence: dict[str, Presence],
    ) -> ConversationPublic:
        """Exposto para a camada de tempo real montar payloads por destinatário."""
        return self._to_public_conversation(conversation, viewer_id, users_by_id, presence)

    async def hydration_context(
        self, conversations: list[Conversation]
    ) -> tuple[dict[str, User], dict[str, Presence]]:
        """Versão pública do contexto de hidratação (usuários + presença)."""
        return await self._hydration_context(conversations)

    def to_public_message(self, message: Message, conversation: Conversation) -> MessagePublic:
        """Exposto para a camada de tempo real montar o payload da mensagem."""
        return self._to_public_message(message, conversation)

    # ----- Internos -----

    async def _require_participant(self, conversation_id: str, user_id: str) -> Conversation:
        conversation = await self._conversations.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError
        if conversation.participant(user_id) is None:
            raise NotAParticipantError
        return conversation

    async def _conversation_for_removal(
        self, conversation_id: str, user_id: str
    ) -> Conversation | None:
        """Carrega a conversa para exclusão/saída.

        Retorna None se ela já não existe (operação idempotente); levanta
        ``NotAParticipantError`` se existe mas o usuário não participa.
        """
        conversation = await self._conversations.get_by_id(conversation_id)
        if conversation is None:
            return None
        if conversation.participant(user_id) is None:
            raise NotAParticipantError
        return conversation

    async def _hydration_context(
        self, conversations: list[Conversation]
    ) -> tuple[dict[str, User], dict[str, Presence]]:
        ids = {pid for conversation in conversations for pid in conversation.participant_ids}
        users = await self._users.get_by_ids(list(ids))
        users_by_id = {user.id: user for user in users}
        presence = await self._presence.presence_for(list(ids))
        return users_by_id, presence

    def _to_public_conversation(
        self,
        conversation: Conversation,
        viewer_id: str,
        users_by_id: dict[str, User],
        presence: dict[str, Presence],
    ) -> ConversationPublic:
        participants = [
            self._to_chat_user(users_by_id[pid], presence)
            for pid in conversation.participant_ids
            if pid in users_by_id
        ]
        viewer = conversation.participant(viewer_id)
        return ConversationPublic(
            id=conversation.id,
            type=conversation.type,
            name=self._display_name(conversation, viewer_id, users_by_id),
            participants=participants,
            last_message=self._preview_message(conversation),
            unread=viewer.unread if viewer else 0,
            favourite=viewer.favourite if viewer else False,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )

    @staticmethod
    def _display_name(
        conversation: Conversation, viewer_id: str, users_by_id: dict[str, User]
    ) -> str:
        if conversation.type is ConversationType.GROUP:
            return conversation.name or "Grupo"
        other_id = next(iter(conversation.other_participant_ids(viewer_id)), None)
        other = users_by_id.get(other_id) if other_id else None
        return other.full_name if other else "Usuário"

    @staticmethod
    def _preview_message(conversation: Conversation) -> MessagePublic | None:
        preview = conversation.last_message
        if not preview:
            return None
        return MessagePublic(
            id=preview.get("id", ""),
            conversation_id=conversation.id,
            sender_id=preview["sender_id"],
            type=MessageType(preview["type"]),
            text=preview.get("text", ""),
            created_at=preview["created_at"],
        )

    def _to_public_message(self, message: Message, conversation: Conversation) -> MessagePublic:
        recipients = conversation.other_participant_ids(message.sender_id)
        deleted = message.deleted_for_everyone
        media = None if deleted else self._media_public(message)
        return MessagePublic(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            type=message.type,
            text="" if deleted else message.text,
            media=media,
            created_at=message.created_at,
            status=message.status_for(recipients),
            read_by=message.read_by,
            delivered_to=message.delivered_to,
            deleted=deleted,
        )

    def _media_public(self, message: Message) -> MediaPublic | None:
        if message.media is None:
            return None
        document = message.media.to_document()
        # URL gerada em tempo de leitura (a partir da chave), quando possível.
        if self._presign is not None:
            document["url"] = self._presign(message.media.key)
        return MediaPublic(**document)

    @staticmethod
    def _to_chat_user(user: User, presence: dict[str, Presence]) -> ChatUser:
        state = presence.get(user.id)
        return ChatUser(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            online=state.online if state else False,
            last_seen=state.last_seen if state else None,
        )


def _noop_delete(user_id: str) -> "DeleteResult":
    """Resultado de uma exclusão idempotente quando não há nada a remover."""
    return DeleteResult(media_keys=[], notify_ids=[user_id], hard_deleted=False)


def _preview_of(message: Message) -> dict[str, object]:
    """Resumo da mensagem armazenado em ``last_message`` para a lista de conversas."""
    text = message.text or _PREVIEW_BY_TYPE.get(message.type, "")
    return {
        "id": message.id,
        "sender_id": message.sender_id,
        "type": message.type.value,
        "text": text,
        "created_at": message.created_at,
    }


def _media_info_from_payload(media: MediaPayload | None) -> MediaInfo | None:
    if media is None:
        return None
    return MediaInfo(
        key=media.key,
        url=media.url,
        mime=media.mime,
        size=media.size,
        name=media.name,
        duration=media.duration,
    )
