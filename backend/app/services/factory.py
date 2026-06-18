"""Fábricas dos serviços do chat com a infraestrutura real (Redis + MinIO).

Centraliza a construção de ``ChatService``, ``PresenceService`` e
``MediaService`` para evitar duplicidade entre a injeção do FastAPI e a camada
de tempo real (Socket.IO), que não usa o sistema de dependências do FastAPI.
"""

from functools import lru_cache

from minio import Minio
from redis.asyncio import Redis

from app.core.config import get_settings
from app.db.mongodb import get_database
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.services.chat_service import ChatService
from app.services.media_service import MediaService
from app.services.presence_service import PresenceService


@lru_cache
def get_redis() -> Redis:
    """Cliente Redis assíncrono (singleton) com respostas decodificadas."""
    return Redis.from_url(get_settings().redis_url, decode_responses=True)


@lru_cache
def get_minio() -> Minio:
    """Cliente MinIO interno (operações na rede do Docker)."""
    return _build_minio(get_settings().minio_endpoint)


@lru_cache
def get_minio_public() -> Minio:
    """Cliente MinIO público — assina URLs acessíveis pelo navegador."""
    return _build_minio(get_settings().minio_public_endpoint)


def _build_minio(endpoint: str) -> Minio:
    settings = get_settings()
    return Minio(
        endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=settings.minio_use_ssl,
        region=settings.minio_region,
    )


def build_presence_service() -> PresenceService:
    return PresenceService(get_redis())


def build_media_service() -> MediaService:
    return MediaService(
        get_minio(), bucket=get_settings().minio_bucket, presigner=get_minio_public()
    )


def build_chat_service() -> ChatService:
    database = get_database()
    return ChatService(
        conversations=ConversationRepository(database),
        messages=MessageRepository(database),
        users=UserRepository(database),
        presence=build_presence_service(),
        presign=build_media_service().presign,
    )
