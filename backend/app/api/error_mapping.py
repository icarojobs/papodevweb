"""Tradução centralizada de erros de domínio para respostas HTTP.

Evita repetir blocos try/except em cada rota (DRY) e mantém um único ponto de
verdade para o mapeamento entre exceções de negócio e códigos HTTP.
"""

from contextlib import contextmanager

from fastapi import HTTPException, status

from app.core.constants import (
    ERR_CANNOT_LEAVE_DIRECT,
    ERR_CONVERSATION_NOT_FOUND,
    ERR_EMPTY_MESSAGE,
    ERR_GROUP_NEEDS_MEMBERS,
    ERR_MEDIA_TOO_LARGE,
    ERR_NOT_A_PARTICIPANT,
    ERR_RECIPIENT_NOT_FOUND,
    ERR_UNSUPPORTED_MEDIA,
)
from app.services.exceptions import (
    CannotLeaveDirectError,
    ConversationNotFoundError,
    DomainError,
    EmptyMessageError,
    GroupNeedsMembersError,
    MediaTooLargeError,
    NotAParticipantError,
    RecipientNotFoundError,
    UnsupportedMediaError,
)

_STATUS_BY_ERROR: dict[type[DomainError], tuple[int, str]] = {
    ConversationNotFoundError: (status.HTTP_404_NOT_FOUND, ERR_CONVERSATION_NOT_FOUND),
    RecipientNotFoundError: (status.HTTP_404_NOT_FOUND, ERR_RECIPIENT_NOT_FOUND),
    NotAParticipantError: (status.HTTP_403_FORBIDDEN, ERR_NOT_A_PARTICIPANT),
    EmptyMessageError: (status.HTTP_400_BAD_REQUEST, ERR_EMPTY_MESSAGE),
    GroupNeedsMembersError: (status.HTTP_400_BAD_REQUEST, ERR_GROUP_NEEDS_MEMBERS),
    CannotLeaveDirectError: (status.HTTP_400_BAD_REQUEST, ERR_CANNOT_LEAVE_DIRECT),
    MediaTooLargeError: (status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, ERR_MEDIA_TOO_LARGE),
    UnsupportedMediaError: (status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, ERR_UNSUPPORTED_MEDIA),
}


@contextmanager
def domain_errors():
    """Converte ``DomainError`` conhecidos em ``HTTPException`` apropriados."""
    try:
        yield
    except DomainError as exc:
        mapping = _STATUS_BY_ERROR.get(type(exc))
        if mapping is None:
            raise
        status_code, detail = mapping
        raise HTTPException(status_code=status_code, detail=detail) from None
