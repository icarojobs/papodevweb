"""Serviço de mídia: upload de objetos (imagens, arquivos, áudio) no MinIO.

O armazenamento é abstraído por um ``Protocol`` compatível com o cliente MinIO,
permitindo injetar um fake nos testes (Inversão de Dependência — SOLID).
"""

import asyncio
import uuid
from datetime import timedelta
from io import BytesIO
from typing import Protocol

from app.core.constants import (
    MAX_AUDIO_BYTES,
    MAX_DOCUMENT_BYTES,
    MAX_IMAGE_BYTES,
    MAX_VIDEO_BYTES,
    PRESIGNED_URL_EXPIRES_SECONDS,
)
from app.schemas.chat import MediaPublic
from app.services.exceptions import MediaTooLargeError, UnsupportedMediaError


def _limit_for(content_type: str) -> int | None:
    """Tamanho máximo (bytes) por categoria de MIME, ou None se não suportado."""
    if content_type.startswith("image/"):
        return MAX_IMAGE_BYTES
    if content_type.startswith("video/"):
        return MAX_VIDEO_BYTES
    if content_type.startswith("audio/"):
        return MAX_AUDIO_BYTES
    if content_type.startswith(("application/", "text/")):
        return MAX_DOCUMENT_BYTES
    return None


class ObjectStorage(Protocol):
    """Subconjunto síncrono da API do cliente MinIO usado pelo serviço."""

    def bucket_exists(self, bucket_name: str) -> bool: ...
    def make_bucket(self, bucket_name: str) -> None: ...
    def put_object(
        self, bucket_name: str, object_name: str, data: BytesIO, length: int, content_type: str
    ) -> object: ...
    def presigned_get_object(self, bucket_name: str, object_name: str, expires: object) -> str: ...
    def remove_object(self, bucket_name: str, object_name: str) -> None: ...


def _sanitize_filename(filename: str) -> str:
    """Mantém apenas o nome final do arquivo (evita path traversal)."""
    return filename.replace("\\", "/").rsplit("/", 1)[-1] or "arquivo"


class MediaService:
    """Faz upload de mídias e devolve seus metadados públicos.

    ``storage`` é usado para operações internas (criar bucket, enviar/remover);
    ``presigner`` assina as URLs de leitura. Eles podem apontar para endpoints
    diferentes: o interno (rede do Docker) e o público (acessível no navegador),
    pois a assinatura SigV4 inclui o host de destino.
    """

    def __init__(
        self, storage: ObjectStorage, *, bucket: str, presigner: ObjectStorage | None = None
    ) -> None:
        self._storage = storage
        self._bucket = bucket
        self._presigner = presigner or storage

    async def ensure_bucket(self) -> None:
        """Garante a existência do bucket (idempotente)."""
        exists = await asyncio.to_thread(self._storage.bucket_exists, self._bucket)
        if not exists:
            await asyncio.to_thread(self._storage.make_bucket, self._bucket)

    @staticmethod
    def _validate(content_type: str, size: int) -> None:
        limit = _limit_for(content_type) if content_type else None
        if limit is None:
            raise UnsupportedMediaError
        if size > limit:
            raise MediaTooLargeError

    async def upload(self, *, data: bytes, content_type: str, filename: str) -> MediaPublic:
        """Valida e envia a mídia, retornando seus metadados públicos."""
        size = len(data)
        self._validate(content_type, size)
        await self.ensure_bucket()

        safe_name = _sanitize_filename(filename)
        key = f"{uuid.uuid4().hex}/{safe_name}"
        await asyncio.to_thread(
            self._storage.put_object,
            self._bucket,
            key,
            BytesIO(data),
            size,
            content_type,
        )
        url = await asyncio.to_thread(self.presign, key)
        return MediaPublic(key=key, url=url, mime=content_type, size=size, name=safe_name)

    def presign(self, key: str) -> str:
        """Gera uma URL de leitura assinada (válida por alguns dias) para a chave.

        Operação offline (sem rede) com a região fixada; pode ser chamada em
        tempo de leitura para que a URL nunca expire de forma permanente nem
        fique presa a um endpoint antigo.
        """
        return self._presigner.presigned_get_object(
            self._bucket, key, timedelta(seconds=PRESIGNED_URL_EXPIRES_SECONDS)
        )

    async def delete(self, keys: list[str]) -> None:
        """Remove os objetos informados do bucket (ignora lista vazia)."""
        for key in keys:
            await asyncio.to_thread(self._storage.remove_object, self._bucket, key)
