"""Agendador do job diário de retenção (00:01) via APScheduler."""

import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.core.constants import RETENTION_CRON_HOUR, RETENTION_CRON_MINUTE
from app.db.mongodb import get_database
from app.jobs.retention import RetentionService
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.factory import build_media_service

logger = logging.getLogger(__name__)

RETENTION_JOB_ID = "retention-purge"


async def run_purge() -> None:
    """Executa o expurgo de retenção sobre o banco atual."""
    database = get_database()
    service = RetentionService(
        conversations=ConversationRepository(database),
        messages=MessageRepository(database),
        media=build_media_service(),
    )
    result = await service.purge(datetime.now(UTC))
    logger.info(
        "Retenção aplicada (corte %s): %s mensagens, %s conversas, %s mídias removidas.",
        result.cutoff.isoformat(),
        result.messages,
        result.conversations,
        result.media,
    )


def build_scheduler() -> AsyncIOScheduler:
    """Cria o agendador com o job diário de retenção às 00:01."""
    timezone = get_settings().scheduler_timezone
    scheduler = AsyncIOScheduler(timezone=timezone)
    scheduler.add_job(
        run_purge,
        CronTrigger(
            hour=RETENTION_CRON_HOUR, minute=RETENTION_CRON_MINUTE, timezone=timezone
        ),
        id=RETENTION_JOB_ID,
        replace_existing=True,
    )
    return scheduler
