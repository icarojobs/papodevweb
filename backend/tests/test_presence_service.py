"""Testes do PresenceService (online / visto por último)."""

from datetime import UTC, datetime

from app.services.presence_service import PresenceService
from tests.fakes import FakePresenceStore


async def test_online_offline_cycle():
    service = PresenceService(FakePresenceStore())
    await service.set_online("u1")

    presence = await service.presence_for(["u1", "u2"])
    assert presence["u1"].online is True
    assert presence["u1"].last_seen is None
    assert presence["u2"].online is False

    moment = datetime(2026, 6, 17, 12, 0, tzinfo=UTC)
    await service.set_offline("u1", now=moment)

    assert await service.last_seen("u1") == moment
    presence = await service.presence_for(["u1"])
    assert presence["u1"].online is False
    assert presence["u1"].last_seen == moment


async def test_last_seen_absent():
    service = PresenceService(FakePresenceStore())
    assert await service.last_seen("desconhecido") is None
