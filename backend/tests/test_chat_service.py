"""Testes unitários do ChatService (regras de negócio do chat)."""

import pytest

from app.core.constants import ConversationType, MessageStatus, MessageType
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.chat import CreateConversationRequest, MediaPayload
from app.services.chat_service import ChatService
from app.services.exceptions import (
    ConversationNotFoundError,
    EmptyMessageError,
    GroupNeedsMembersError,
    NotAParticipantError,
    RecipientNotFoundError,
)


async def _make_user(repository: UserRepository, full_name: str, email: str) -> User:
    return await repository.create(
        full_name=full_name, email=email, hashed_password="x", is_active=True
    )


async def _direct(chat_service, owner_id: str, recipient_id: str):
    return await chat_service.create_conversation(
        owner_id, CreateConversationRequest(recipient_id=recipient_id)
    )


# ----- Busca de usuários -----


async def test_search_users_by_name_and_email_excluding_self(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice Silva", "alice@example.com")
    await _make_user(user_repository, "Bruno Souza", "bruno@example.com")

    by_name = await chat_service.search_users("bruno", requester_id=alice.id)
    by_email = await chat_service.search_users("BRUNO@example", requester_id=alice.id)
    self_search = await chat_service.search_users("Alice", requester_id=alice.id)

    assert [u.full_name for u in by_name] == ["Bruno Souza"]
    assert [u.email for u in by_email] == ["bruno@example.com"]
    assert self_search == []


async def test_search_users_ignores_inactive(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    await user_repository.create(
        full_name="Inativo", email="inativo@example.com", hashed_password="x", is_active=False
    )
    results = await chat_service.search_users("Inativo", requester_id=alice.id)
    assert results == []


# ----- Criação de conversas -----


async def test_create_direct_is_idempotent(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")

    first = await _direct(chat_service, alice.id, bob.id)
    second = await _direct(chat_service, bob.id, alice.id)

    assert first.id == second.id
    assert first.type is ConversationType.DIRECT
    # Nome exibido é relativo a quem vê.
    assert first.name == "Bob"
    assert second.name == "Alice"


@pytest.mark.parametrize("recipient", ["", None, "000000000000000000000000", "self"])
async def test_create_direct_invalid_recipient(chat_service, user_repository, recipient):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    recipient_id = alice.id if recipient == "self" else recipient
    with pytest.raises(RecipientNotFoundError):
        await chat_service.create_conversation(
            alice.id, CreateConversationRequest(recipient_id=recipient_id)
        )


async def test_create_group(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    carol = await _make_user(user_repository, "Carol", "carol@example.com")

    group = await chat_service.create_conversation(
        alice.id,
        CreateConversationRequest(
            type=ConversationType.GROUP, name="Equipe", member_ids=[bob.id, carol.id]
        ),
    )

    assert group.type is ConversationType.GROUP
    assert group.name == "Equipe"
    assert {p.id for p in group.participants} == {alice.id, bob.id, carol.id}


async def test_create_group_without_members_fails(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    with pytest.raises(GroupNeedsMembersError):
        await chat_service.create_conversation(
            alice.id,
            CreateConversationRequest(type=ConversationType.GROUP, name="Vazio", member_ids=[]),
        )


async def test_create_group_default_name(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    group = await chat_service.create_conversation(
        alice.id,
        CreateConversationRequest(type=ConversationType.GROUP, member_ids=[bob.id]),
    )
    assert group.name == "Novo grupo"


# ----- Envio e leitura de mensagens -----


async def test_send_and_list_messages(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)

    result = await chat_service.send_message(conversation.id, alice.id, text="Olá Bob!")

    assert result.message.text == "Olá Bob!"
    # Status inicial: enviado (Bob ainda não recebeu/leu).
    public = chat_service.to_public_message(result.message, result.conversation)
    assert public.status is MessageStatus.SENT

    messages = await chat_service.get_messages(conversation.id, bob.id)
    assert [m.text for m in messages] == ["Olá Bob!"]

    # Não-lido incrementa para Bob, não para Alice.
    listed = await chat_service.list_conversations(bob.id)
    assert listed[0].unread == 1
    listed_alice = await chat_service.list_conversations(alice.id)
    assert listed_alice[0].unread == 0
    assert listed_alice[0].last_message.text == "Olá Bob!"


async def test_send_empty_message_fails(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    with pytest.raises(EmptyMessageError):
        await chat_service.send_message(conversation.id, alice.id, text="   ")


async def test_send_media_message_preview(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)

    media = MediaPayload(
        key="k", url="http://m/k", mime="image/png", size=10, name="foto.png"
    )
    result = await chat_service.send_message(
        conversation.id, alice.id, type=MessageType.IMAGE, media=media
    )

    public = chat_service.to_public_message(result.message, result.conversation)
    assert public.media is not None
    assert public.media.url == "http://m/k"
    listed = await chat_service.list_conversations(bob.id)
    assert listed[0].last_message.text == "📷 Foto"


async def test_send_to_unknown_conversation(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    with pytest.raises(ConversationNotFoundError):
        await chat_service.send_message("000000000000000000000000", alice.id, text="oi")


async def test_send_when_not_participant(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    intruder = await _make_user(user_repository, "Eve", "eve@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    with pytest.raises(NotAParticipantError):
        await chat_service.send_message(conversation.id, intruder.id, text="intruso")


async def test_mark_read_updates_status_and_unread(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    sent = await chat_service.send_message(conversation.id, alice.id, text="Oi")

    read = await chat_service.mark_read(conversation.id, bob.id)
    assert sent.message.id in read.message_ids

    # Sob a ótica de Alice, a mensagem agora está lida.
    messages = await chat_service.get_messages(conversation.id, alice.id)
    assert messages[0].status is MessageStatus.READ
    # Não-lido de Bob foi zerado.
    listed = await chat_service.list_conversations(bob.id)
    assert listed[0].unread == 0


async def test_mark_delivered_updates_status(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    await chat_service.send_message(conversation.id, alice.id, text="Oi")

    delivered_ids = await chat_service.mark_delivered(conversation.id, bob.id)
    assert len(delivered_ids) == 1

    messages = await chat_service.get_messages(conversation.id, alice.id)
    assert messages[0].status is MessageStatus.DELIVERED


async def test_toggle_favourite(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)

    assert await chat_service.toggle_favourite(conversation.id, alice.id) is True
    assert await chat_service.toggle_favourite(conversation.id, alice.id) is False
    # Favorito é por usuário: Bob continua sem favoritar.
    listed_bob = await chat_service.list_conversations(bob.id)
    assert listed_bob[0].favourite is False


async def test_list_conversations_reflects_presence(
    chat_service, user_repository, presence_service
):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    await _direct(chat_service, alice.id, bob.id)
    await presence_service.set_online(bob.id)

    listed = await chat_service.list_conversations(alice.id)
    bob_entry = next(p for p in listed[0].participants if p.id == bob.id)
    assert bob_entry.online is True


async def test_get_messages_requires_participant(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    eve = await _make_user(user_repository, "Eve", "eve@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    with pytest.raises(NotAParticipantError):
        await chat_service.get_messages(conversation.id, eve.id)


async def test_get_conversation_unknown(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    with pytest.raises(ConversationNotFoundError):
        await chat_service.get_conversation("000000000000000000000000", alice.id)


async def test_media_url_generated_at_read_time(
    conversation_repository, message_repository, user_repository, presence_service
):
    # ChatService com resolver de URL: a URL deve ser regenerada a partir da
    # chave, ignorando a URL (possivelmente expirada) gravada na mensagem.
    service = ChatService(
        conversations=conversation_repository,
        messages=message_repository,
        users=user_repository,
        presence=presence_service,
        presign=lambda key: f"signed://{key}",
    )
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(service, alice.id, bob.id)
    media = MediaPayload(
        key="kX", url="http://host-antigo/kX", mime="image/png", size=1, name="x.png"
    )

    result = await service.send_message(
        conversation.id, alice.id, type=MessageType.IMAGE, media=media
    )
    public = service.to_public_message(result.message, result.conversation)

    assert public.media is not None
    assert public.media.url == "signed://kX"

    # E também no histórico carregado.
    messages = await service.get_messages(conversation.id, bob.id)
    assert messages[0].media.url == "signed://kX"
