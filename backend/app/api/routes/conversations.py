"""Rotas de conversas: listar, criar, histórico de mensagens e favoritar."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_chat_service, get_current_user, get_media_service
from app.api.error_mapping import domain_errors
from app.core.constants import DEFAULT_MESSAGE_PAGE_SIZE, MAX_MESSAGE_PAGE_SIZE, DeleteScope
from app.models.user import User
from app.schemas.chat import (
    ConversationPublic,
    CreateConversationRequest,
    FavouriteResponse,
    MessagePublic,
)
from app.services.chat_service import ChatService
from app.services.media_service import MediaService

router = APIRouter(prefix="/conversations", tags=["conversations"])

CurrentUser = Annotated[User, Depends(get_current_user)]
Service = Annotated[ChatService, Depends(get_chat_service)]
Media = Annotated[MediaService, Depends(get_media_service)]


@router.get("", response_model=list[ConversationPublic])
async def list_conversations(
    current_user: CurrentUser, service: Service
) -> list[ConversationPublic]:
    """Lista as conversas do usuário, da mais recente para a mais antiga."""
    return await service.list_conversations(current_user.id)


@router.post("", response_model=ConversationPublic, status_code=201)
async def create_conversation(
    payload: CreateConversationRequest, current_user: CurrentUser, service: Service
) -> ConversationPublic:
    """Cria (ou reaproveita) uma conversa direta, ou cria um grupo."""
    with domain_errors():
        return await service.create_conversation(current_user.id, payload)


@router.get("/{conversation_id}", response_model=ConversationPublic)
async def get_conversation(
    conversation_id: str, current_user: CurrentUser, service: Service
) -> ConversationPublic:
    with domain_errors():
        return await service.get_conversation(conversation_id, current_user.id)


@router.get("/{conversation_id}/messages", response_model=list[MessagePublic])
async def list_messages(
    conversation_id: str,
    current_user: CurrentUser,
    service: Service,
    before: Annotated[datetime | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_MESSAGE_PAGE_SIZE)] = DEFAULT_MESSAGE_PAGE_SIZE,
) -> list[MessagePublic]:
    """Histórico paginado de uma conversa (ordem cronológica)."""
    with domain_errors():
        return await service.get_messages(
            conversation_id, current_user.id, before=before, limit=limit
        )


@router.patch("/{conversation_id}/favourite", response_model=FavouriteResponse)
async def toggle_favourite(
    conversation_id: str, current_user: CurrentUser, service: Service
) -> FavouriteResponse:
    """Alterna o estado de favorito da conversa para o usuário."""
    with domain_errors():
        favourite = await service.toggle_favourite(conversation_id, current_user.id)
    return FavouriteResponse(favourite=favourite)


@router.post("/{conversation_id}/leave", status_code=204)
async def leave_group(
    conversation_id: str, current_user: CurrentUser, service: Service, media: Media
) -> None:
    """Sai de um grupo; remove o grupo e suas mídias se ficar vazio."""
    with domain_errors():
        result = await service.leave_group(conversation_id, current_user.id)
    await media.delete(result.media_keys)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser,
    service: Service,
    media: Media,
    scope: Annotated[DeleteScope, Query()] = DeleteScope.ME,
    delete_media: Annotated[bool, Query()] = False,
) -> None:
    """Exclui a conversa (só para mim ou para todos), purgando mídia se solicitado."""
    with domain_errors():
        result = await service.delete_conversation(
            conversation_id, current_user.id, scope=scope, delete_media=delete_media
        )
    await media.delete(result.media_keys)
