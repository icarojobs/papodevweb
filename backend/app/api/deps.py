"""Dependências do FastAPI (injeção de repositórios, serviços e usuário atual)."""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import BEARER_SCHEME, ERR_INVALID_TOKEN, TokenType
from app.core.security import decode_token
from app.db.mongodb import get_database
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.email_service import send_email_verification_email, send_password_reset_email

EmailSender = Callable[[str, str], Awaitable[None]]


def get_email_sender() -> EmailSender:
    """Fornece o remetente do e-mail de redefinição (substituível em testes)."""
    return send_password_reset_email


def get_verification_email_sender() -> EmailSender:
    """Fornece o remetente do e-mail de confirmação (substituível em testes)."""
    return send_email_verification_email


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
