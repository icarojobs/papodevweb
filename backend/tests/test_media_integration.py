"""Testes de integração de mídia contra um S3 simulado (Moto).

Sobe um servidor S3 em memória com ``moto`` e aponta o cliente MinIO real do
``MediaService`` para ele, exercitando o fluxo completo: envio (upload),
recebimento (download via URL assinada) e exclusão. A persistência é verificada
de forma independente com ``boto3``.
"""

import socket

import boto3
import httpx
import pytest
from botocore.exceptions import ClientError
from minio import Minio
from moto.server import ThreadedMotoServer

from app.core.constants import MAX_IMAGE_BYTES
from app.services.exceptions import MediaTooLargeError
from app.services.media_service import MediaService

_BUCKET = "papodevweb-integ"
_ACCESS = "testkey"
_SECRET = "testsecret"


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def s3_endpoint():
    """Servidor S3 simulado (Moto) ativo durante o módulo de testes."""
    port = _free_port()
    server = ThreadedMotoServer(ip_address="127.0.0.1", port=port)
    server.start()
    yield f"127.0.0.1:{port}"
    server.stop()


@pytest.fixture
def minio_client(s3_endpoint) -> Minio:
    return Minio(
        s3_endpoint,
        access_key=_ACCESS,
        secret_key=_SECRET,
        secure=False,
        region="us-east-1",
    )


@pytest.fixture
def boto_client(s3_endpoint):
    return boto3.client(
        "s3",
        endpoint_url=f"http://{s3_endpoint}",
        aws_access_key_id=_ACCESS,
        aws_secret_access_key=_SECRET,
        region_name="us-east-1",
    )


@pytest.fixture
def media_service(minio_client) -> MediaService:
    return MediaService(minio_client, bucket=_BUCKET)


async def test_upload_download_delete_roundtrip(media_service, boto_client):
    data = b"conteudo-binario-da-imagem-0123456789"

    # Envio: faz o upload e cria o bucket (idempotente).
    media = await media_service.upload(
        data=data, content_type="image/png", filename="dir/foto.png"
    )
    assert media.name == "foto.png"
    assert media.mime == "image/png"
    assert media.size == len(data)

    # Persistência verificada de forma independente com boto3.
    stored = boto_client.get_object(Bucket=_BUCKET, Key=media.key)["Body"].read()
    assert stored == data

    # Recebimento: download pela URL assinada devolve exatamente o conteúdo.
    response = httpx.get(media.url)
    assert response.status_code == 200
    assert response.content == data

    # Exclusão remove o objeto do bucket.
    await media_service.delete([media.key])
    with pytest.raises(ClientError):
        boto_client.get_object(Bucket=_BUCKET, Key=media.key)


async def test_document_roundtrip(media_service):
    data = b"%PDF-1.4 conteudo de documento"
    media = await media_service.upload(
        data=data, content_type="application/pdf", filename="contrato.pdf"
    )
    assert media.name == "contrato.pdf"
    response = httpx.get(media.url)
    assert response.status_code == 200
    assert response.content == data


async def test_oversized_image_is_rejected_before_upload(media_service, boto_client):
    await media_service.ensure_bucket()
    with pytest.raises(MediaTooLargeError):
        await media_service.upload(
            data=b"x" * (MAX_IMAGE_BYTES + 1), content_type="image/png", filename="grande.png"
        )
    # Nenhum objeto "grande" foi enviado ao bucket.
    listing = boto_client.list_objects_v2(Bucket=_BUCKET, Prefix="")
    keys = [obj["Key"] for obj in listing.get("Contents", [])]
    assert all("grande.png" not in key for key in keys)
