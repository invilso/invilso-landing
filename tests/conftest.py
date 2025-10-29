from __future__ import annotations

import httpx
import pytest
import pytest_asyncio

from app.config import get_settings
from app.factory import create_app


class DummyRedis:
    def __init__(self) -> None:
        self.jobs: list[tuple[str, dict[str, str]]] = []
        self.closed: bool = False

    async def enqueue_job(self, name: str, payload: dict[str, str]):
        self.jobs.append((name, payload))
        return f"{name}-job"

    async def close(self) -> None:
        self.closed = True


@pytest.fixture
def dummy_redis() -> DummyRedis:
    return DummyRedis()


@pytest.fixture(autouse=True)
def reset_settings(monkeypatch: pytest.MonkeyPatch):
    get_settings.cache_clear()
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "0")
    monkeypatch.setenv("REDIS_HOST", "redis")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_DB", "0")
    monkeypatch.delenv("REDIS_PASSWORD", raising=False)
    try:
        yield
    finally:
        get_settings.cache_clear()


@pytest_asyncio.fixture
async def client(dummy_redis: DummyRedis):
    async def factory():
        return dummy_redis

    app = create_app(redis_pool_factory=factory)
    lifespan = app.router.lifespan_context(app)
    await lifespan.__aenter__()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as async_client:
            yield async_client
    finally:
        await lifespan.__aexit__(None, None, None)
