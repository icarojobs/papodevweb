"""Testes da orquestração de tempo real (ChatRealtime) e do handshake."""

import pytest

from app.core.constants import SocketEvent
from app.realtime import socket as socket_module
from app.realtime.handlers import ChatRealtime
from app.schemas.chat import CreateConversationRequest


class FakeSio:
    """Servidor Socket.IO falso que registra emissões e salas."""

    def __init__(self) -> None:
        self.emitted: list[tuple[str, dict, str | None]] = []
        self.rooms: list[tuple[str, str]] = []

    async def emit(self, event, data, room=None) -> None:
        self.emitted.append((str(event), data, room))

    async def enter_room(self, sid, room) -> None:
        self.rooms.append((sid, room))

    def events(self, name: SocketEvent) -> list[tuple[str, dict, str | None]]:
        return [item for item in self.emitted if item[0] == name.value]


async def _make_user(user_repository, full_name, email):
    return await user_repository.create(
        full_name=full_name, email=email, hashed_password="x", is_active=True
    )


@pytest.fixture
async def scenario(chat_service, user_repository):
    alice = await _make_user(user_repository, "Alice", "alice@example.com")
    bob = await _make_user(user_repository, "Bob", "bob@example.com")
    conversation = await chat_service.create_conversation(
        alice.id, CreateConversationRequest(recipient_id=bob.id)
    )
    return {"alice": alice, "bob": bob, "conversation": conversation}


@pytest.fixture
def realtime(chat_service, presence_service):
    sio = FakeSio()
    return ChatRealtime(sio, chat_service=chat_service, presence_service=presence_service), sio


async def test_on_send_broadcasts_message_and_conversation(realtime, scenario):
    handler, sio = realtime
    ack = await handler.on_send(
        scenario["alice"].id,
        {"conversation_id": scenario["conversation"].id, "type": "text", "text": "Olá"},
    )
    assert ack["ok"] is True
    new_events = sio.events(SocketEvent.MESSAGE_NEW)
    rooms = {room for _, _, room in new_events}
    assert rooms == {f"user:{scenario['alice'].id}", f"user:{scenario['bob'].id}"}
    assert len(sio.events(SocketEvent.CONVERSATION_UPDATED)) == 2


async def test_on_send_invalid_payload(realtime, scenario):
    handler, _ = realtime
    ack = await handler.on_send(scenario["alice"].id, {"text": "sem conversa"})
    assert ack["ok"] is False


async def test_on_send_domain_error(realtime, scenario, user_repository):
    handler, _ = realtime
    eve = await _make_user(user_repository, "Eve", "eve@example.com")
    ack = await handler.on_send(
        eve.id, {"conversation_id": scenario["conversation"].id, "text": "intruso"}
    )
    assert ack["ok"] is False


async def test_on_connect_delivers_and_announces_presence(realtime, scenario, chat_service):
    handler, sio = realtime
    # Bob envia para Alice; ao conectar, Alice deve receber a entrega marcada.
    await chat_service.send_message(
        scenario["conversation"].id, scenario["bob"].id, text="oi Alice"
    )
    await handler.on_connect(scenario["alice"].id)

    assert sio.events(SocketEvent.MESSAGE_STATUS), "deveria emitir recibo de entrega"
    presence = sio.events(SocketEvent.PRESENCE)
    assert any(data["online"] is True for _, data, _ in presence)


async def test_on_disconnect_announces_offline(realtime, scenario):
    handler, sio = realtime
    await handler.on_disconnect(scenario["alice"].id)
    presence = sio.events(SocketEvent.PRESENCE)
    assert presence
    assert all(data["online"] is False for _, data, _ in presence)


async def test_on_open_enters_room_and_marks_read(realtime, scenario, chat_service):
    handler, sio = realtime
    await chat_service.send_message(
        scenario["conversation"].id, scenario["bob"].id, text="oi"
    )
    await handler.on_open("sid-1", scenario["alice"].id, scenario["conversation"].id)

    assert ("sid-1", f"conv:{scenario['conversation'].id}") in sio.rooms
    read_events = sio.events(SocketEvent.MESSAGE_STATUS)
    assert any(data["status"] == "read" for _, data, _ in read_events)


async def test_on_read_without_messages_still_updates(realtime, scenario):
    handler, sio = realtime
    await handler.on_read(scenario["alice"].id, scenario["conversation"].id)
    # Sem mensagens pendentes: nenhum recibo, mas a conversa é atualizada.
    assert sio.events(SocketEvent.MESSAGE_STATUS) == []
    assert sio.events(SocketEvent.CONVERSATION_UPDATED)


async def test_on_read_domain_error_is_silent(realtime, user_repository):
    handler, sio = realtime
    eve = await _make_user(user_repository, "Eve", "eve@example.com")
    await handler.on_read(eve.id, "000000000000000000000000")
    assert sio.emitted == []


async def test_on_typing_notifies_others_only(realtime, scenario):
    handler, sio = realtime
    await handler.on_typing(
        scenario["alice"].id, scenario["conversation"].id, True
    )
    typing = sio.events(SocketEvent.TYPING)
    rooms = {room for _, _, room in typing}
    assert rooms == {f"user:{scenario['bob'].id}"}


async def test_on_typing_domain_error_is_silent(realtime, user_repository):
    handler, sio = realtime
    eve = await _make_user(user_repository, "Eve", "eve@example.com")
    await handler.on_typing(eve.id, "000000000000000000000000", True)
    assert sio.events(SocketEvent.TYPING) == []


async def test_on_delete_message_everyone_broadcasts_and_purges(
    scenario, chat_service, presence_service
):
    purged: list[list[str]] = []

    async def purge(keys):
        purged.append(keys)

    sio = FakeSio()
    handler = ChatRealtime(
        sio, chat_service=chat_service, presence_service=presence_service, media_purge=purge
    )
    from app.core.constants import MessageType
    from app.schemas.chat import MediaPayload

    sent = await chat_service.send_message(
        scenario["conversation"].id,
        scenario["alice"].id,
        type=MessageType.IMAGE,
        media=MediaPayload(key="kZ", url="u", mime="image/png", size=1, name="z.png"),
    )
    ack = await handler.on_delete_message(
        scenario["alice"].id,
        {
            "conversation_id": scenario["conversation"].id,
            "message_id": sent.message.id,
            "scope": "everyone",
        },
    )
    assert ack["ok"] is True
    assert purged == [["kZ"]]
    rooms = {room for _, _, room in sio.events(SocketEvent.MESSAGE_DELETED)}
    assert rooms == {f"user:{scenario['alice'].id}", f"user:{scenario['bob'].id}"}
    assert sio.events(SocketEvent.CONVERSATION_UPDATED)


async def test_on_delete_message_me_notifies_only_user(realtime, scenario, chat_service):
    handler, sio = realtime
    sent = await chat_service.send_message(
        scenario["conversation"].id, scenario["alice"].id, text="oi"
    )
    ack = await handler.on_delete_message(
        scenario["bob"].id,
        {
            "conversation_id": scenario["conversation"].id,
            "message_id": sent.message.id,
            "scope": "me",
        },
    )
    assert ack["ok"] is True
    rooms = {room for _, _, room in sio.events(SocketEvent.MESSAGE_DELETED)}
    assert rooms == {f"user:{scenario['bob'].id}"}


async def test_on_delete_message_invalid_payload(realtime, scenario):
    handler, _ = realtime
    ack = await handler.on_delete_message(
        scenario["alice"].id, {"conversation_id": scenario["conversation"].id}
    )
    assert ack["ok"] is False


async def test_connect_rejects_invalid_token():
    accepted = await socket_module.connect("sid", {}, {"token": "invalido"})
    assert accepted is False


async def test_session_user_missing(monkeypatch):
    async def boom(_sid):
        raise KeyError

    monkeypatch.setattr(socket_module.sio, "get_session", boom)
    assert await socket_module._session_user("x") is None
