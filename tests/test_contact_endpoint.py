from __future__ import annotations

from contextlib import asynccontextmanager
from types import SimpleNamespace

import httpx
import pytest

from app.config import get_settings
from app.factory import create_app
from app.services.rate_limit import resolve_client_ip, reset_rate_limit_service
from app.services.telegram import send_telegram_message
from app.workers import registry
from tests.conftest import DummyRedis


@asynccontextmanager
async def lifespan_client(app):
    lifespan = app.router.lifespan_context(app)
    await lifespan.__aenter__()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as async_client:
            yield async_client
    finally:
        await lifespan.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_contact_endpoint_enqueues_job(client: httpx.AsyncClient, dummy_redis: DummyRedis) -> None:
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "message": "This is a sufficiently long test message."
    }

    response = await client.post("/api/contact", json=payload)

    assert response.status_code == httpx.codes.ACCEPTED
    assert response.json() == {"queued": True}
    job_name = registry.job_name(send_telegram_message)
    assert dummy_redis.jobs == [(job_name, payload)]


@pytest.mark.asyncio
async def test_contact_endpoint_rate_limits(client: httpx.AsyncClient, dummy_redis: DummyRedis) -> None:
    payload = {
        "name": "Rate Limited",
        "email": "rate@example.com",
        "message": "Message content exceeding the minimum length requirements."
    }

    for _ in range(3):
        response = await client.post("/api/contact", json=payload)
        assert response.status_code == httpx.codes.ACCEPTED

    response = await client.post("/api/contact", json=payload)

    assert response.status_code == httpx.codes.TOO_MANY_REQUESTS
    assert "Too many contact requests" in response.json()["detail"]


@pytest.mark.asyncio
async def test_contact_endpoint_rate_limits_with_forwarded_header(client: httpx.AsyncClient) -> None:
    payload = {
        "name": "Header Limited",
        "email": "header@example.com",
        "message": "Message body that is long enough to pass validation requirements."
    }
    headers = {"X-Forwarded-For": "203.0.113.10, 203.0.113.11"}

    for _ in range(3):
        response = await client.post("/api/contact", json=payload, headers=headers)
        assert response.status_code == httpx.codes.ACCEPTED

    response = await client.post("/api/contact", json=payload, headers=headers)

    assert response.status_code == httpx.codes.TOO_MANY_REQUESTS


def test_resolve_client_identifier_prefers_forwarded_for() -> None:
    request = SimpleNamespace(headers={"x-forwarded-for": "198.51.100.1, 198.51.100.2"}, client=SimpleNamespace(host="127.0.0.1"))
    assert resolve_client_ip(request) == "198.51.100.1"  # type: ignore[arg-type]


def test_resolve_client_identifier_falls_back_to_client_host() -> None:
    request = SimpleNamespace(headers={}, client=SimpleNamespace(host="203.0.113.5"))
    assert resolve_client_ip(request) == "203.0.113.5"  # type: ignore[arg-type]


def test_resolve_client_identifier_handles_missing_client() -> None:
    request = SimpleNamespace(headers={}, client=None)
    assert resolve_client_ip(request) == "unknown"  # type: ignore[arg-type]


def test_reset_rate_limits_defaults_to_memory_storage() -> None:
    reset_rate_limit_service()


@pytest.mark.asyncio
async def test_contact_endpoint_missing_queue_returns_503(dummy_redis: DummyRedis) -> None:
    payload = {
        "name": "Queue Missing",
        "email": "missing@example.com",
        "message": "Attempting to trigger unavailable queue error."
    }

    async def factory():
        return dummy_redis

    app = create_app(redis_pool_factory=factory)
    async with lifespan_client(app) as async_client:
        app.state.redis = None
        response = await async_client.post("/api/contact", json=payload)

    assert response.status_code == httpx.codes.SERVICE_UNAVAILABLE
    assert response.json()["detail"] == "Job queue unavailable."


@pytest.mark.asyncio
async def test_root_serves_static_index(client: httpx.AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == httpx.codes.OK
    assert "Send Message" in response.text


@pytest.mark.asyncio
async def test_app_uses_default_pool_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_settings = {}
    dummy_pool = DummyRedis()

    async def fake_create_pool(redis_settings):
        captured_settings["settings"] = redis_settings
        return dummy_pool

    monkeypatch.setattr("app.factory.create_pool", fake_create_pool)

    app = create_app()
    async with lifespan_client(app) as async_client:
        response = await async_client.get("/")
        assert response.status_code == httpx.codes.OK

    assert dummy_pool.closed is True
    settings = get_settings()
    assert captured_settings["settings"].host == settings.redis_host


class SyncCloseRedis:
    def __init__(self) -> None:
        self.closed = False

    async def enqueue_job(self, name: str, payload: dict[str, str]):
        return name, payload

    def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_app_handles_synchronous_close() -> None:
    sync_pool = SyncCloseRedis()

    async def factory():
        return sync_pool

    app = create_app(redis_pool_factory=factory)
    async with lifespan_client(app) as async_client:
        await async_client.get("/")

    assert sync_pool.closed is True
