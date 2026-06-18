"""Rota de upload de mídia (imagens, arquivos e áudio) para o MinIO."""

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import get_current_user, get_media_service
from app.api.error_mapping import domain_errors
from app.core.constants import APPLICATION_OCTET_STREAM
from app.models.user import User
from app.schemas.chat import UploadResponse
from app.services.media_service import MediaService

router = APIRouter(prefix="/media", tags=["media"])


@router.post("", response_model=UploadResponse, status_code=201)
async def upload_media(
    file: UploadFile,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[MediaService, Depends(get_media_service)],
) -> UploadResponse:
    """Recebe um arquivo e devolve seus metadados públicos após o upload."""
    data = await file.read()
    content_type = file.content_type or APPLICATION_OCTET_STREAM
    with domain_errors():
        media = await service.upload(
            data=data, content_type=content_type, filename=file.filename or "arquivo"
        )
    return UploadResponse(**media.model_dump())
