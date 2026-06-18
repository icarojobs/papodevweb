"""Testes da exclusão de mensagem individual (para mim / para todos)."""

import pytest

from app.core.constants import MSG_MESSAGE_DELETED, DeleteScope, MessageType
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.chat import CreateConversationRequest, MediaPayload
from app.services.exceptions import (
    CannotDeleteForEveryoneError,
    MessageNotFoundError,
    NotAParticipantError,
)

_IMAGE = MediaPayload(key="mkey", url="http://m/mkey", mime="image/png", size=10, name="f.png")


async def _make_user(repository: UserRepository, full_name: str, email: str) -> User:
    return await repository.create(
        full_name=full_name, email=email, hashed_password="x", is_active=True
    )


async def _direct(chat_service, owner_id: str, recipient_id: str):
    return await chat_service.create_conversation(
        owner_id, CreateConversationRequest(recipient_id=recipient_id)
    )


async def test_delete_for_me_hides_only_for_user(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    sent = await chat_service.send_message(conversation.id, bob.id, text="oi alice")

    result = await chat_service.delete_message(
        conversation.id, sent.message.id, alice.id, scope=DeleteScope.ME
    )
    assert result.scope is DeleteScope.ME
    assert result.media_keys == []

    # Some para Alice, permanece para Bob.
    assert await chat_service.get_messages(conversation.id, alice.id) == []
    bob_view = await chat_service.get_messages(conversation.id, bob.id)
    assert [m.text for m in bob_view] == ["oi alice"]


async def test_delete_for_everyone_tombstones_and_purges(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    sent = await chat_service.send_message(
        conversation.id, alice.id, type=MessageType.IMAGE, media=_IMAGE
    )

    result = await chat_service.delete_message(
        conversation.id, sent.message.id, alice.id, scope=DeleteScope.EVERYONE
    )
    assert result.scope is DeleteScope.EVERYONE
    assert result.media_keys == ["mkey"]
    assert set(result.notify_ids) == {alice.id, bob.id}

    # Vira tombstone para todos (texto vazio, mídia nula, deleted=True).
    for viewer in (alice.id, bob.id):
        messages = await chat_service.get_messages(conversation.id, viewer)
        assert len(messages) == 1
        assert messages[0].deleted is True
        assert messages[0].media is None
        assert messages[0].text == ""

    # A prévia da conversa reflete o tombstone.
    listed = await chat_service.list_conversations(bob.id)
    assert listed[0].last_message.text == MSG_MESSAGE_DELETED


async def test_delete_for_everyone_only_sender(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    sent = await chat_service.send_message(conversation.id, alice.id, text="da alice")

    # Bob não pode apagar para todos uma mensagem de Alice.
    with pytest.raises(CannotDeleteForEveryoneError):
        await chat_service.delete_message(
            conversation.id, sent.message.id, bob.id, scope=DeleteScope.EVERYONE
        )


async def test_delete_message_not_found(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    with pytest.raises(MessageNotFoundError):
        await chat_service.delete_message(
            conversation.id, "000000000000000000000000", alice.id, scope=DeleteScope.ME
        )


async def test_delete_message_requires_participant(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    eve = await _make_user(user_repository, "Eve", "eve@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    sent = await chat_service.send_message(conversation.id, alice.id, text="oi")
    with pytest.raises(NotAParticipantError):
        await chat_service.delete_message(
            conversation.id, sent.message.id, eve.id, scope=DeleteScope.ME
        )


async def test_message_repo_hide_and_delete_invalid_id(message_repository):
    assert await message_repository.get_by_id("ruim") is None
    assert await message_repository.hide_for_user("ruim", "u1") is False
    assert await message_repository.delete_for_everyone("ruim") is None
