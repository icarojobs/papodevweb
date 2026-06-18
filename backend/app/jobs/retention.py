"""Retenção de histórico: expurga conversas/mensagens/mídias com mais de 7 dias.

A política mantém, de forma global, apenas os últimos ``RETENTION_DAYS`` dias:
conversas sem atividade desde o corte são removidas por completo e mensagens
antigas (em qualquer conversa) são apagadas junto com seus objetos no MinIO.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.constants import RETENTION_DAYS
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.media_service import MediaService


@dataclass
class PurgeResult:
    """Quantidades removidas em uma execução do expurgo."""

    cutoff: datetime
    messages: int
    conversations: int
    media: int


class RetentionService:
    """Aplica a política de retenção sobre conversas, mensagens e mídias."""

    def __init__(
        self,
        *,
        conversations: ConversationRepository,
        messages: MessageRepository,
        media: MediaService,
        retention_days: int = RETENTION_DAYS,
    ) -> None:
        self._conversations = conversations
        self._messages = messages
        self._media = media
        self._retention_days = retention_days

    async def purge(self, now: datetime) -> PurgeResult:
        """Remove o que excede a janela de retenção. Retorna as contagens."""
        cutoff = now - timedelta(days=self._retention_days)
        # Coleta as chaves de mídia antes de apagar as mensagens.
        media_keys = await self._messages.media_keys_before(cutoff)
        deleted_messages = await self._messages.delete_before(cutoff)
        deleted_conversations = await self._conversations.delete_stale_before(cutoff)
        await self._media.delete(media_keys)
        return PurgeResult(
            cutoff=cutoff,
            messages=deleted_messages,
            conversations=deleted_conversations,
            media=len(media_keys),
        )
