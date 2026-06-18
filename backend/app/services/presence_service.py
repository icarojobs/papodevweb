"""Serviço de presença (online / visto por último) apoiado no Redis.

Depende apenas de um subconjunto da interface do cliente Redis assíncrono, o
que permite injetar um fake em testes (Inversão de Dependência — SOLID).
"""

from datetime import datetime
from typing import Protocol

from app.core.constants import PRESENCE_LAST_SEEN_HASH, PRESENCE_ONLINE_SET


class PresenceStore(Protocol):
    """Subconjunto assíncrono do cliente Redis usado pela presença."""

    async def sadd(self, name: str, *values: str) -> int: ...
    async def srem(self, name: str, *values: str) -> int: ...
    async def smembers(self, name: str) -> set[str]: ...
    async def hset(self, name: str, key: str, value: str) -> int: ...
    async def hget(self, name: str, key: str) -> str | None: ...


class Presence:
    """Estado de presença de um usuário."""

    def __init__(self, *, online: bool, last_seen: datetime | None) -> None:
        self.online = online
        self.last_seen = last_seen


class PresenceService:
    """Registra e consulta a presença dos usuários."""

    def __init__(self, store: PresenceStore) -> None:
        self._store = store

    async def set_online(self, user_id: str) -> None:
        await self._store.sadd(PRESENCE_ONLINE_SET, user_id)

    async def set_offline(self, user_id: str, *, now: datetime) -> None:
        await self._store.srem(PRESENCE_ONLINE_SET, user_id)
        await self._store.hset(PRESENCE_LAST_SEEN_HASH, user_id, now.isoformat())

    async def last_seen(self, user_id: str) -> datetime | None:
        raw = await self._store.hget(PRESENCE_LAST_SEEN_HASH, user_id)
        return datetime.fromisoformat(raw) if raw else None

    async def presence_for(self, user_ids: list[str]) -> dict[str, Presence]:
        """Mapeia cada usuário ao seu estado de presença atual."""
        online = await self._store.smembers(PRESENCE_ONLINE_SET)
        result: dict[str, Presence] = {}
        for user_id in user_ids:
            is_online = user_id in online
            last_seen = None if is_online else await self.last_seen(user_id)
            result[user_id] = Presence(online=is_online, last_seen=last_seen)
        return result
