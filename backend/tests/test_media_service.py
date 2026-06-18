"""Testes do MediaService (upload de mídia com armazenamento fake)."""

import pytest

from app.core.constants import (
    MAX_AUDIO_BYTES,
    MAX_DOCUMENT_BYTES,
    MAX_IMAGE_BYTES,
    MAX_VIDEO_BYTES,
)
from app.services.exceptions import MediaTooLargeError, UnsupportedMediaError
from app.services.media_service import MediaService, _limit_for, _sanitize_filename
from tests.fakes import FakeStorage

_BUCKET = "papodevweb-test"


def test_sanitize_filename():
    assert _sanitize_filename("../../etc/passwd") == "passwd"
    assert _sanitize_filename("") == "arquivo"
    assert _sanitize_filename("foto.png") == "foto.png"


async def test_upload_creates_bucket_and_object():
    storage = FakeStorage(existing=False)
    service = MediaService(storage, bucket=_BUCKET)

    media = await service.upload(
        data=b"conteudo", content_type="image/png", filename="dir/foto.png"
    )

    assert media.name == "foto.png"
    assert media.size == len(b"conteudo")
    assert media.mime == "image/png"
    assert media.url.endswith(media.key)
    assert _BUCKET in storage.made_buckets
    assert media.key in storage.objects


async def test_upload_signs_url_with_presigner():
    # O objeto é gravado no storage interno, mas a URL é assinada pelo presigner
    # (endpoint público), que pode apontar para outro host.
    storage = FakeStorage(existing=True)
    presigner = FakeStorage(existing=True)
    presigner.presigned_get_object = (  # type: ignore[method-assign]
        lambda bucket, key, expires: f"http://public.local/{bucket}/{key}"
    )
    service = MediaService(storage, bucket=_BUCKET, presigner=presigner)

    media = await service.upload(data=b"x", content_type="image/png", filename="f.png")

    assert media.url.startswith("http://public.local/")
    assert media.key in storage.objects


def test_presign_uses_presigner():
    presigner = FakeStorage(existing=True)
    service = MediaService(FakeStorage(), bucket=_BUCKET, presigner=presigner)
    url = service.presign("dir/foto.png")
    assert url == f"http://minio.local/{_BUCKET}/dir/foto.png"


async def test_upload_skips_bucket_creation_when_exists():
    storage = FakeStorage(existing=True)
    service = MediaService(storage, bucket=_BUCKET)
    await service.upload(data=b"x", content_type="audio/ogg", filename="a.ogg")
    assert storage.made_buckets == []


def test_limit_for_categories():
    assert _limit_for("image/png") == MAX_IMAGE_BYTES
    assert _limit_for("video/mp4") == MAX_VIDEO_BYTES
    assert _limit_for("audio/webm") == MAX_AUDIO_BYTES
    assert _limit_for("application/pdf") == MAX_DOCUMENT_BYTES
    assert _limit_for("text/plain") == MAX_DOCUMENT_BYTES
    assert _limit_for("font/woff") is None


@pytest.mark.parametrize(
    ("content_type", "limit"),
    [
        ("image/png", MAX_IMAGE_BYTES),
        ("application/pdf", MAX_DOCUMENT_BYTES),
    ],
)
async def test_upload_rejects_oversized_by_type(content_type, limit):
    service = MediaService(FakeStorage(existing=True), bucket=_BUCKET)
    with pytest.raises(MediaTooLargeError):
        await service.upload(
            data=b"x" * (limit + 1), content_type=content_type, filename="big.bin"
        )


async def test_upload_accepts_video_and_audio():
    service = MediaService(FakeStorage(existing=True), bucket=_BUCKET)
    video = await service.upload(data=b"x" * 1024, content_type="video/mp4", filename="v.mp4")
    audio = await service.upload(data=b"x" * 1024, content_type="audio/webm", filename="a.webm")
    assert video.mime == "video/mp4"
    assert audio.mime == "audio/webm"


@pytest.mark.parametrize("content_type", ["", "weird/type", "font/woff"])
async def test_upload_rejects_unsupported_media(content_type):
    service = MediaService(FakeStorage(existing=True), bucket=_BUCKET)
    with pytest.raises(UnsupportedMediaError):
        await service.upload(data=b"x", content_type=content_type, filename="x.bin")
