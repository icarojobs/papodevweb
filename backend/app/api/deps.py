"""Dependências do FastAPI (injeção de repositórios, serviços e usuário atual)."""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import BEARER_SCHEME, ERR_ADMIN_REQUIRED, ERR_INVALID_TOKEN, TokenType
from app.core.security import decode_token
from app.db.mongodb import get_database
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.settings_repository import SettingsRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.email_service import (
    send_email_verification_email,
    send_password_reset_email,
    send_test_email,
)
from app.services.factory import build_media_service, build_presence_service
from app.services.media_service import MediaService
from app.services.presence_service import PresenceService
from app.services.settings_service import SettingsService

EmailSender = Callable[[str, str], Awaitable[None]]
TestEmailSender = Callable[[str], Awaitable[None]]


def get_email_sender() -> EmailSender:
    """Fornece o remetente do e-mail de redefinição (substituível em testes)."""
    return send_password_reset_email


def get_verification_email_sender() -> EmailSender:
    """Fornece o remetente do e-mail de confirmação (substituível em testes)."""
    return send_email_verification_email


def get_test_email_sender() -> TestEmailSender:
    """Fornece o remetente do e-mail de teste do /admin (substituível em testes)."""
    return send_test_email


def get_db() -> AsyncIOMotorDatabase:
    return get_database()


def get_user_repository(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> UserRepository:
    return UserRepository(database)


def get_auth_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(repository)


def get_conversation_repository(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> ConversationRepository:
    return ConversationRepository(database)


def get_message_repository(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> MessageRepository:
    return MessageRepository(database)


def get_presence_service() -> PresenceService:
    """Serviço de presença (Redis). Substituível por um fake em testes."""
    return build_presence_service()


def get_media_service() -> MediaService:
    """Serviço de mídia (MinIO). Substituível por um fake em testes."""
    return build_media_service()


def get_chat_service(
    conversations: Annotated[ConversationRepository, Depends(get_conversation_repository)],
    messages: Annotated[MessageRepository, Depends(get_message_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
    presence: Annotated[PresenceService, Depends(get_presence_service)],
    media: Annotated[MediaService, Depends(get_media_service)],
) -> ChatService:
    return ChatService(
        conversations=conversations,
        messages=messages,
        users=users,
        presence=presence,
        presign=media.presign,
    )


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith(f"{BEARER_SCHEME} "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERR_INVALID_TOKEN,
            headers={"WWW-Authenticate": BEARER_SCHEME},
        )
    return authorization.removeprefix(f"{BEARER_SCHEME} ").strip()


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    repository: Annotated[UserRepository, Depends(get_user_repository)] = None,  # type: ignore[assignment]
) -> User:
    """Resolve o usuário autenticado a partir do access token do header."""
    token = _extract_bearer_token(authorization)
    subject = decode_token(token, TokenType.ACCESS)
    user = await repository.get_by_id(subject) if subject else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERR_INVALID_TOKEN,
            headers={"WWW-Authenticate": BEARER_SCHEME},
        )
    return user


async def get_current_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Garante que o usuário autenticado é administrador (acesso ao /admin)."""
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERR_ADMIN_REQUIRED)
    return user


def get_settings_service(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> SettingsService:
    """Serviço de configurações da plataforma (e-mail de disparo)."""
    return SettingsService(SettingsRepository(database))
