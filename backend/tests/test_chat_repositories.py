"""Testes dos repositórios de chat e do utilitário de ObjectId."""

from datetime import UTC, datetime

from app.core.constants import ConversationType, MessageType
from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.object_id import to_object_id, to_object_ids


def test_to_object_id_invalid():
    assert to_object_id("não-é-id") is None
    assert to_object_id(None) is None  # type: ignore[arg-type]


def test_to_object_ids_filters_invalid():
    valid = "0123456789abcdef01234567"
    assert [str(o) for o in to_object_ids([valid, "ruim"])] == [valid]


async def test_user_get_by_ids_empty_and_invalid(user_repository):
    assert await user_repository.get_by_ids([]) == []
    assert await user_repository.get_by_ids(["ruim"]) == []


async def test_conversation_find_direct_between_none(conversation_repository):
    assert await conversation_repository.find_direct_between("a", "b") is None


async def test_conversation_get_by_id_invalid(conversation_repository):
    assert await conversation_repository.get_by_id("id-invalido") is None


def test_message_status_for_no_recipients():
    from app.core.constants import MessageStatus

    message = Message.from_document(
        Message.new_document(
            conversation_id="c1", sender_id="u1", type=MessageType.TEXT, text="oi"
        )
        | {"_id": "000000000000000000000000"}
    )
    assert message.status_for([]) is MessageStatus.SENT


async def test_conversation_bump_and_reset(conversation_repository):
    document = Conversation.new_document(
        type=ConversationType.DIRECT,
        participant_ids=["u1", "u2"],
        created_by="u1",
    )
    conversation = await conversation_repository.create(document)

    now = datetime.now(UTC)
    await conversation_repository.bump_after_message(
        conversation,
        last_message={"sender_id": "u1", "type": "text", "text": "oi", "created_at": now},
        sender_id="u1",
        now=now,
    )
    updated = await conversation_repository.get_by_id(conversation.id)
    assert updated.participant("u2").unread == 1
    assert updated.participant("u1").unread == 0
    assert updated.last_message["text"] == "oi"

    assert await conversation_repository.reset_unread(conversation.id, "u2", now=now) is True
    refreshed = await conversation_repository.get_by_id(conversation.id)
    assert refreshed.participant("u2").unread == 0


async def test_conversation_reset_unread_unknown(conversation_repository):
    assert (
        await conversation_repository.reset_unread(
            "000000000000000000000000", "u1", now=datetime.now(UTC)
        )
        is False
    )


async def test_conversation_set_favourite_unknown(conversation_repository):
    assert (
        await conversation_repository.set_favourite("000000000000000000000000", "u1", True)
        is False
    )


async def test_update_last_message_text_noop(conversation_repository):
    # Conversa inexistente: no-op silencioso.
    await conversation_repository.update_last_message_text("000000000000000000000000", "x")
    # Conversa sem prévia (last_message None): permanece sem prévia.
    document = Conversation.new_document(
        type=ConversationType.DIRECT, participant_ids=["u1", "u2"], created_by="u1"
    )
    conversation = await conversation_repository.create(document)
    await conversation_repository.update_last_message_text(conversation.id, "x")
    refreshed = await conversation_repository.get_by_id(conversation.id)
    assert refreshed.last_message is None


async def test_conversation_update_invalid_id_is_noop(conversation_repository):
    # Não deve lançar exceção mesmo com id inválido.
    await conversation_repository._update("id-invalido", {"name": "x"})


async def test_message_list_pagination_and_before(message_repository):
    base = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    for index in range(3):
        document = Message.new_document(
            conversation_id="c1", sender_id="u1", type=MessageType.TEXT, text=f"m{index}"
        )
        document["created_at"] = base.replace(minute=index)
        await message_repository.create(document)

    todas = await message_repository.list_for_conversation("c1")
    assert [m.text for m in todas] == ["m0", "m1", "m2"]

    page = await message_repository.list_for_conversation("c1", limit=2)
    assert [m.text for m in page] == ["m1", "m2"]

    older = await message_repository.list_for_conversation(
        "c1", before=base.replace(minute=2)
    )
    assert [m.text for m in older] == ["m0", "m1"]


async def test_message_mark_delivered_and_read(message_repository):
    document = Message.new_document(
        conversation_id="c1", sender_id="u1", type=MessageType.TEXT, text="oi"
    )
    await message_repository.create(document)

    delivered = await message_repository.mark_delivered("c1", "u2")
    assert len(delivered) == 1
    # Idempotente: já entregue, nada pendente.
    assert await message_repository.mark_delivered("c1", "u2") == []

    read = await message_repository.mark_read("c1", "u2")
    assert len(read) == 1
    assert await message_repository.mark_read("c1", "u2") == []
