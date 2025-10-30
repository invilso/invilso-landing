from __future__ import annotations

import asyncio

import pytest
from limits.aio.storage import MemoryStorage

from app.services import rate_limit


@pytest.mark.asyncio
async def test_get_rate_limit_service_initializes_once(monkeypatch: pytest.MonkeyPatch) -> None:
    memory_storage = MemoryStorage()
    monkeypatch.setattr(rate_limit, "_rate_limit_service", None, raising=False)
    monkeypatch.setattr(rate_limit, "_rate_limit_service_lock", asyncio.Lock(), raising=False)
    monkeypatch.setattr(rate_limit, "_build_redis_storage", lambda: memory_storage, raising=False)

    service = await rate_limit.get_rate_limit_service()
    assert service.storage is memory_storage

    second_service = await rate_limit.get_rate_limit_service()
    assert second_service is service


def test_build_redis_storage_includes_password(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_uri: dict[str, str] = {}

    class DummyStorage:
        def __init__(self, uri: str) -> None:
            captured_uri["uri"] = uri

    monkeypatch.setenv("REDIS_PASSWORD", "super-secret")
    monkeypatch.setenv("REDIS_HOST", "cache")
    monkeypatch.setenv("REDIS_PORT", "6380")
    monkeypatch.setenv("REDIS_DB", "2")
    monkeypatch.setattr(rate_limit, "RedisStorage", DummyStorage)
    rate_limit.get_settings.cache_clear()

    storage = rate_limit._build_redis_storage()

    assert isinstance(storage, DummyStorage)
    assert captured_uri["uri"] == "redis://:super-secret@cache:6380/2"
