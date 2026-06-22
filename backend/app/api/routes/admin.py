"""Rotas administrativas (/admin) — restritas a usuários admin.

Configuração do e-mail de disparo (SMTP) da plataforma.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    TestEmailSender,
    get_current_admin,
    get_settings_service,
    get_test_email_sender,
)
from app.core.constants import (
    ERR_EMAIL_SETTINGS_NOT_CONFIGURED,
    ERR_TEST_EMAIL_FAILED,
    MSG_TEST_EMAIL_SENT,
)
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.settings import EmailSettingsPublic, EmailSettingsUpdate, TestEmailRequest
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/admin", tags=["admin"])

# Todas as rotas exigem admin.
AdminUser = Annotated[User, Depends(get_current_admin)]
Settings = Annotated[SettingsService, Depends(get_settings_service)]


@router.get("/settings/email", response_model=EmailSettingsPublic)
async def get_email_settings(_admin: AdminUser, service: Settings) -> EmailSettingsPublic:
    """Retorna a configuração do e-mail de disparo (sem a senha)."""
    return await service.get_email_settings()


@router.put("/settings/email", response_model=EmailSettingsPublic)
async def update_email_settings(
    payload: EmailSettingsUpdate, _admin: AdminUser, service: Settings
) -> EmailSettingsPublic:
    """Salva a configuração do e-mail de disparo (senha write-only)."""
    return await service.update_email_settings(payload)


@router.post("/settings/email/test", response_model=MessageResponse)
async def send_test_email(
    payload: TestEmailRequest,
    _admin: AdminUser,
    service: Settings,
    sender: Annotated[TestEmailSender, Depends(get_test_email_sender)],
) -> MessageResponse:
    """Envia um e-mail de teste com a configuração efetiva (valida o SMTP)."""
    config = await service.get_effective_email_config()
    if not config.host:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERR_EMAIL_SETTINGS_NOT_CONFIGURED
        )
    try:
        await sender(str(payload.to))
    except Exception as exc:  # noqa: BLE001 — qualquer falha de SMTP vira 502 amigável
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=ERR_TEST_EMAIL_FAILED
        ) from exc
    return MessageResponse(message=MSG_TEST_EMAIL_SENT)
