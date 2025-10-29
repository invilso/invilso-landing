from __future__ import annotations

import pytest

from app.config import get_settings
from app.services.telegram import send_telegram_message
from app.worker import WorkerSettings
from app.workers import worker_shutdown, worker_startup


def test_worker_settings_configuration() -> None:
    settings = get_settings()

    assert WorkerSettings.redis_settings.host == settings.redis_host
    assert WorkerSettings.redis_settings.port == settings.redis_port
    assert WorkerSettings.functions == [send_telegram_message]
    assert WorkerSettings.keep_result == 0


@pytest.mark.asyncio
async def test_worker_module_lifecycle_bridge() -> None:
    ctx: dict[str, object] = {}
    await worker_startup(ctx)
    assert "http_client" in ctx
    await worker_shutdown(ctx)
    assert "http_client" not in ctx
