"""Rotas de usuários: busca para iniciar conversas."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_chat_service, get_current_user
from app.core.constants import MAX_SEARCH_RESULTS, MIN_SEARCH_QUERY_LENGTH
from app.models.user import User
from app.schemas.chat import ChatUser
from app.services.chat_service import ChatService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/search", response_model=list[ChatUser])
async def search_users(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ChatService, Depends(get_chat_service)],
    q: Annotated[
        str, Query(min_length=MIN_SEARCH_QUERY_LENGTH, max_length=MAX_SEARCH_RESULTS * 10)
    ],
) -> list[ChatUser]:
    """Busca usuários ativos por nome ou e-mail (exceto o próprio)."""
    return await service.search_users(q, requester_id=current_user.id)
