"""Testes do serviço de retenção (expurgo de histórico/mídia com +7 dias)."""

from datetime import UTC, datetime, timedelta

from app.core.constants import ConversationType, MessageType
from app.jobs.retention import RetentionService
from app.models.conversation import Conversation
from app.models.message import MediaInfo, Message
from app.services.media_service import MediaService
from tests.fakes import FakeStorage

_NOW = datetime(2026, 6, 18, 12, 0, tzinfo=UTC)
_OLD = _NOW - timedelta(days=10)
_RECENT = _NOW - timedelta(hours=1)


def _conversation_doc(participant_ids: list[str], updated_at: datetime) -> dict:
    return {
        **Conversation.new_document(
            type=ConversationType.DIRECT, participant_ids=participant_ids, created_by="u1"
        ),
        "updated_at": updated_at,
    }


def _message_doc(conversation_id: str, created_at: datetime, *, media_key: str | None) -> dict:
    media = (
        MediaInfo(key=media_key, url="u", mime="image/png", size=1, name="x")
        if media_key
        else None
    )
    message_type = MessageType.IMAGE if media_key else MessageType.TEXT
    return {
        **Message.new_document(
            conversation_id=conversation_id,
            sender_id="u1",
            type=message_type,
            text="oi",
            media=media,
        ),
        "created_at": created_at,
    }


async def test_purge_removes_old_keeps_recent(conversation_repository, message_repository):
    storage = FakeStorage(existing=True)
    storage.objects["old1"] = ("b", 1, "image/png")
    storage.objects["old2"] = ("b", 1, "image/png")
    service = RetentionService(
        conversations=conversation_repository,
        messages=message_repository,
        media=MediaService(storage, bucket="b"),
    )

    active = await conversation_repository.create(_conversation_doc(["u1", "u2"], _RECENT))
    await message_repository.create(_message_doc(active.id, _OLD, media_key="old1"))
    await message_repository.create(_message_doc(active.id, _RECENT, media_key=None))

    stale = await conversation_repository.create(_conversation_doc(["u1", "u3"], _OLD))
    await message_repository.create(_message_doc(stale.id, _OLD, media_key="old2"))

    result = await service.purge(_NOW)

    assert result.cutoff == _NOW - timedelta(days=7)
    assert result.messages == 2
    assert result.conversations == 1
    assert result.media == 2
    assert "old1" not in storage.objects
    assert "old2" not in storage.objects

    # Conversa ativa mantida, só com a mensagem recente.
    assert await conversation_repository.get_by_id(active.id) is not None
    remaining = await message_repository.list_for_conversation(active.id)
    assert [m.text for m in remaining] == ["oi"]
    # Conversa inativa removida por completo.
    assert await conversation_repository.get_by_id(stale.id) is None


async def test_purge_noop_when_everything_recent(conversation_repository, message_repository):
    service = RetentionService(
        conversations=conversation_repository,
        messages=message_repository,
        media=MediaService(FakeStorage(existing=True), bucket="b"),
    )
    conversation = await conversation_repository.create(_conversation_doc(["u1", "u2"], _RECENT))
    await message_repository.create(_message_doc(conversation.id, _RECENT, media_key=None))

    result = await service.purge(_NOW)

    assert result.messages == 0
    assert result.conversations == 0
    assert result.media == 0


async def test_message_media_keys_before_ignores_textonly(message_repository):
    await message_repository.create(_message_doc("c1", _OLD, media_key=None))
    await message_repository.create(_message_doc("c1", _OLD, media_key="k"))
    keys = await message_repository.media_keys_before(_NOW)
    assert keys == ["k"]
