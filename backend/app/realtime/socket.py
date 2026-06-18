"""Servidor Socket.IO para chat em tempo real.

Usa Redis como gerenciador de mensagens (pub/sub), permitindo escalar o
backend horizontalmente sem perder eventos entre instâncias. A lógica de chat
vive em :class:`~app.realtime.handlers.ChatRealtime`; aqui ficam apenas a
autenticação do handshake e o roteamento dos eventos.
"""

import socketio

from app.core.config import get_settings
from app.core.constants import ROOM_USER_PREFIX, SocketEvent, TokenType
from app.core.security import decode_token
from app.realtime.handlers import ChatRealtime
from app.services.factory import build_chat_service, build_media_service, build_presence_service

_settings = get_settings()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[_settings.frontend_origin],
    client_manager=socketio.AsyncRedisManager(_settings.redis_url),
)


def _build_realtime() -> ChatRealtime:
    """Monta a orquestração de tempo real com a infraestrutura atual."""
    return ChatRealtime(
        sio,
        chat_service=build_chat_service(),
        presence_service=build_presence_service(),
        media_purge=build_media_service().delete,
    )


async def _session_user(sid: str) -> str | None:
    """Recupera o id do usuário associado a uma sessão de socket."""
    try:
        session = await sio.get_session(sid)
    except KeyError:
        return None
    return session.get("user_id")


@sio.event
async def connect(sid: str, environ: dict, auth: dict | None) -> bool:
    """Autentica o socket pelo access token enviado no handshake."""
    token = (auth or {}).get("token", "")
    user_id = decode_token(token, TokenType.ACCESS) if token else None
    if user_id is None:
        return False  # rejeita a conexão
    await sio.save_session(sid, {"user_id": user_id})
    await sio.enter_room(sid, f"{ROOM_USER_PREFIX}{user_id}")
    await _build_realtime().on_connect(user_id)
    return True


@sio.event
async def disconnect(sid: str) -> None:
    """Marca o usuário offline ao desconectar."""
    user_id = await _session_user(sid)
    if user_id is not None:
        await _build_realtime().on_disconnect(user_id)


@sio.on(SocketEvent.CONVERSATION_OPEN.value)
async def conversation_open(sid: str, data: dict) -> None:
    user_id = await _session_user(sid)
    if user_id and isinstance(data, dict) and data.get("conversation_id"):
        await _build_realtime().on_open(sid, user_id, data["conversation_id"])


@sio.on(SocketEvent.MESSAGE_SEND.value)
async def message_send(sid: str, data: dict) -> dict:
    user_id = await _session_user(sid)
    if not user_id or not isinstance(data, dict):
        return {"ok": False, "error": "unauthorized"}
    return await _build_realtime().on_send(user_id, data)


@sio.on(SocketEvent.MESSAGE_READ.value)
async def message_read(sid: str, data: dict) -> None:
    user_id = await _session_user(sid)
    if user_id and isinstance(data, dict) and data.get("conversation_id"):
        await _build_realtime().on_read(user_id, data["conversation_id"])


@sio.on(SocketEvent.MESSAGE_DELETE.value)
async def message_delete(sid: str, data: dict) -> dict:
    user_id = await _session_user(sid)
    if not user_id or not isinstance(data, dict):
        return {"ok": False, "error": "unauthorized"}
    return await _build_realtime().on_delete_message(user_id, data)


@sio.on(SocketEvent.TYPING.value)
async def typing(sid: str, data: dict) -> None:
    user_id = await _session_user(sid)
    if user_id and isinstance(data, dict) and data.get("conversation_id"):
        await _build_realtime().on_typing(
            user_id, data["conversation_id"], bool(data.get("typing"))
        )


def build_asgi_app(fastapi_app) -> socketio.ASGIApp:
    """Combina o FastAPI com o Socket.IO em uma única aplicação ASGI."""
    return socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
