"""Servidor Socket.IO para chat em tempo real.

Usa Redis como gerenciador de mensagens (pub/sub), permitindo escalar o
backend horizontalmente sem perder eventos entre instâncias.
"""

import socketio

from app.core.config import get_settings
from app.core.constants import TokenType
from app.core.security import decode_token

_settings = get_settings()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[_settings.frontend_origin],
    client_manager=socketio.AsyncRedisManager(_settings.redis_url),
)


@sio.event
async def connect(sid: str, environ: dict, auth: dict | None) -> bool:
    """Autentica o socket pelo access token enviado no handshake."""
    token = (auth or {}).get("token", "")
    user_id = decode_token(token, TokenType.ACCESS) if token else None
    if user_id is None:
        return False  # rejeita a conexão
    await sio.save_session(sid, {"user_id": user_id})
    await sio.enter_room(sid, f"user:{user_id}")
    return True


@sio.event
async def disconnect(sid: str) -> None:
    """Encerramento da conexão (hook para presença/limpeza futura)."""


def build_asgi_app(fastapi_app) -> socketio.ASGIApp:
    """Combina o FastAPI com o Socket.IO em uma única aplicação ASGI."""
    return socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="socket.io")
