"""Fakes em memória para as dependências de infraestrutura (Redis e MinIO)."""

from io import BytesIO


class FakePresenceStore:
    """Implementação em memória do subconjunto Redis usado pela presença."""

    def __init__(self) -> None:
        self.sets: dict[str, set[str]] = {}
        self.hashes: dict[str, dict[str, str]] = {}

    async def sadd(self, name: str, *values: str) -> int:
        bucket = self.sets.setdefault(name, set())
        before = len(bucket)
        bucket.update(values)
        return len(bucket) - before

    async def srem(self, name: str, *values: str) -> int:
        bucket = self.sets.setdefault(name, set())
        removed = 0
        for value in values:
            if value in bucket:
                bucket.remove(value)
                removed += 1
        return removed

    async def smembers(self, name: str) -> set[str]:
        return set(self.sets.get(name, set()))

    async def hset(self, name: str, key: str, value: str) -> int:
        self.hashes.setdefault(name, {})[key] = value
        return 1

    async def hget(self, name: str, key: str) -> str | None:
        return self.hashes.get(name, {}).get(key)


class FakeStorage:
    """Implementação em memória do subconjunto da API do cliente MinIO."""

    def __init__(self, *, existing: bool = False) -> None:
        self.objects: dict[str, tuple[str, int, str]] = {}
        self.made_buckets: list[str] = []
        self._bucket_exists = existing

    def bucket_exists(self, bucket_name: str) -> bool:
        return self._bucket_exists

    def make_bucket(self, bucket_name: str) -> None:
        self._bucket_exists = True
        self.made_buckets.append(bucket_name)

    def put_object(
        self, bucket_name: str, object_name: str, data: BytesIO, length: int, content_type: str
    ) -> object:
        self.objects[object_name] = (bucket_name, length, content_type)
        return object()

    def presigned_get_object(self, bucket_name: str, object_name: str, expires: object) -> str:
        return f"http://minio.local/{bucket_name}/{object_name}"

    def remove_object(self, bucket_name: str, object_name: str) -> None:
        self.objects.pop(object_name, None)
