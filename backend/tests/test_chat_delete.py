"""Testes de saída de grupo e exclusão de conversa (per-user e global)."""

import asyncio

import pytest

from app.core.constants import ConversationType, DeleteScope, MessageType
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.chat import CreateConversationRequest, MediaPayload
from app.services.exceptions import (
    CannotLeaveDirectError,
    ConversationNotFoundError,
    NotAParticipantError,
)

_IMAGE = MediaPayload(key="k1", url="http://m/k1", mime="image/png", size=10, name="f.png")


async def _make_user(repository: UserRepository, full_name: str, email: str) -> User:
    return await repository.create(
        full_name=full_name, email=email, hashed_password="x", is_active=True
    )


async def _direct(chat_service, owner_id: str, recipient_id: str):
    return await chat_service.create_conversation(
        owner_id, CreateConversationRequest(recipient_id=recipient_id)
    )


async def _group(chat_service, owner_id: str, member_ids: list[str], name: str = "Grupo"):
    return await chat_service.create_conversation(
        owner_id,
        CreateConversationRequest(
            type=ConversationType.GROUP, name=name, member_ids=member_ids
        ),
    )


# ----- Sair de grupo -----


async def test_leave_group_keeps_for_others(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    carol = await _make_user(user_repository, "Carol", "carol@example.com")
    group = await _group(chat_service, alice.id, [bob.id, carol.id])

    result = await chat_service.leave_group(group.id, alice.id)

    assert result.hard_deleted is False
    assert set(result.notify_ids) == {bob.id, carol.id}
    # Alice não vê mais; Bob continua vendo.
    assert await chat_service.list_conversations(alice.id) == []
    assert len(await chat_service.list_conversations(bob.id)) == 1


async def test_leave_group_last_member_purges(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    group = await _group(chat_service, alice.id, [bob.id])
    await chat_service.send_message(group.id, alice.id, type=MessageType.IMAGE, media=_IMAGE)

    await chat_service.leave_group(group.id, alice.id)
    result = await chat_service.leave_group(group.id, bob.id)

    assert result.hard_deleted is True
    assert result.media_keys == ["k1"]
    with pytest.raises(ConversationNotFoundError):
        await chat_service.get_conversation(group.id, bob.id)


async def test_leave_direct_is_rejected(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    with pytest.raises(CannotLeaveDirectError):
        await chat_service.leave_group(conversation.id, alice.id)


# ----- Excluir conversa: só para mim -----


async def test_delete_for_me_hides_and_clears_history(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    await chat_service.send_message(conversation.id, bob.id, text="mensagem antiga")

    result = await chat_service.delete_conversation(
        conversation.id, alice.id, scope=DeleteScope.ME, delete_media=False
    )
    assert result.hard_deleted is False
    assert await chat_service.list_conversations(alice.id) == []
    # Bob mantém a conversa.
    assert len(await chat_service.list_conversations(bob.id)) == 1


async def test_delete_for_me_then_reappears_without_old_history(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    await chat_service.send_message(conversation.id, bob.id, text="antiga")

    await chat_service.delete_conversation(
        conversation.id, alice.id, scope=DeleteScope.ME, delete_media=False
    )
    # Datetimes têm precisão de milissegundo; garante que "nova" venha depois
    # do marco de limpeza (em produção as mensagens chegam segundos depois).
    await asyncio.sleep(0.01)
    # Nova mensagem faz a conversa reaparecer para Alice.
    await chat_service.send_message(conversation.id, bob.id, text="nova")

    listed = await chat_service.list_conversations(alice.id)
    assert len(listed) == 1
    messages = await chat_service.get_messages(conversation.id, alice.id)
    assert [m.text for m in messages] == ["nova"]


async def test_delete_for_me_with_media_returns_own_keys(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    await chat_service.send_message(conversation.id, alice.id, type=MessageType.IMAGE, media=_IMAGE)
    await chat_service.send_message(
        conversation.id,
        bob.id,
        type=MessageType.IMAGE,
        media=MediaPayload(key="k2", url="u", mime="image/png", size=1, name="b.png"),
    )

    result = await chat_service.delete_conversation(
        conversation.id, alice.id, scope=DeleteScope.ME, delete_media=True
    )
    # Apenas a mídia enviada pela própria Alice.
    assert result.media_keys == ["k1"]


async def test_delete_for_me_last_participant_hard_deletes(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    await chat_service.send_message(conversation.id, alice.id, type=MessageType.IMAGE, media=_IMAGE)

    await chat_service.delete_conversation(
        conversation.id, alice.id, scope=DeleteScope.ME, delete_media=False
    )
    result = await chat_service.delete_conversation(
        conversation.id, bob.id, scope=DeleteScope.ME, delete_media=False
    )
    assert result.hard_deleted is True
    assert "k1" in result.media_keys
    with pytest.raises(ConversationNotFoundError):
        await chat_service.get_conversation(conversation.id, alice.id)


# ----- Excluir conversa: para todos -----


async def test_delete_for_everyone_purges(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    await chat_service.send_message(conversation.id, alice.id, type=MessageType.IMAGE, media=_IMAGE)

    result = await chat_service.delete_conversation(
        conversation.id, alice.id, scope=DeleteScope.EVERYONE, delete_media=True
    )
    assert result.hard_deleted is True
    assert result.media_keys == ["k1"]
    assert set(result.notify_ids) == {alice.id, bob.id}
    assert await chat_service.list_conversations(bob.id) == []


async def test_delete_for_everyone_without_media(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    await chat_service.send_message(conversation.id, alice.id, type=MessageType.IMAGE, media=_IMAGE)

    result = await chat_service.delete_conversation(
        conversation.id, alice.id, scope=DeleteScope.EVERYONE, delete_media=False
    )
    assert result.media_keys == []


async def test_delete_missing_conversation_is_noop(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    # Excluir uma conversa inexistente não deve falhar (idempotente).
    result = await chat_service.delete_conversation(
        "000000000000000000000000", alice.id, scope=DeleteScope.ME, delete_media=True
    )
    assert result.hard_deleted is False
    assert result.media_keys == []


async def test_leave_missing_conversation_is_noop(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    result = await chat_service.leave_group("000000000000000000000000", alice.id)
    assert result.hard_deleted is False


async def test_delete_requires_participant(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    eve = await _make_user(user_repository, "Eve", "eve@example.com")
    conversation = await _direct(chat_service, alice.id, bob.id)
    with pytest.raises(NotAParticipantError):
        await chat_service.delete_conversation(
            conversation.id, eve.id, scope=DeleteScope.ME, delete_media=False
        )


# ----- Repositórios e mídia -----


async def test_remove_participant_unknown_conversation(conversation_repository):
    assert await conversation_repository.remove_participant("000000000000000000000000", "u") == 0


async def test_mark_deleted_for_unknown_conversation(conversation_repository):
    from datetime import UTC, datetime

    assert (
        await conversation_repository.mark_deleted_for(
            "000000000000000000000000", "u", now=datetime.now(UTC)
        )
        == 0
    )


async def test_message_media_keys_and_delete(message_repository):
    from app.models.message import MediaInfo, Message

    document = Message.new_document(
        conversation_id="c1",
        sender_id="u1",
        type=MessageType.IMAGE,
        media=MediaInfo(key="kk", url="u", mime="image/png", size=1, name="x"),
    )
    await message_repository.create(document)
    await message_repository.create(
        Message.new_document(conversation_id="c1", sender_id="u2", type=MessageType.TEXT, text="oi")
    )

    assert await message_repository.media_keys("c1") == ["kk"]
    assert await message_repository.media_keys("c1", sender_id="u2") == []
    assert await message_repository.delete_by_conversation("c1") == 2


async def test_media_service_delete():
    from app.services.media_service import MediaService
    from tests.fakes import FakeStorage

    storage = FakeStorage(existing=True)
    storage.objects["a/x.png"] = ("b", 1, "image/png")
    service = MediaService(storage, bucket="b")
    await service.delete(["a/x.png"])
    assert "a/x.png" not in storage.objects
