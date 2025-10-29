from __future__ import annotations

import json
from typing import Any, Dict

import httpx
import pytest

from app.services.telegram import send_telegram_message, worker_shutdown, worker_startup


@pytest.mark.asyncio
async def test_worker_startup_and_shutdown() -> None:
    ctx: dict[str, object] = {}
    await worker_startup(ctx)

    client = ctx.get("http_client")
    assert isinstance(client, httpx.AsyncClient)

    await worker_shutdown(ctx)
    assert "http_client" not in ctx


@pytest.mark.asyncio
async def test_send_telegram_message_posts_payload() -> None:
    captured_request: Dict[str, Any] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured_request["url"] = str(request.url)
        captured_request["json"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    ctx = {"http_client": httpx.AsyncClient(transport=transport)}

    payload = {"name": "Tester", "email": "tester@example.com", "message": "Hello there!"}
    await send_telegram_message(ctx, payload)

    await ctx["http_client"].aclose()

    url = captured_request["url"]
    assert isinstance(url, str) and "api.telegram.org" in url

    request_json = captured_request["json"]
    assert isinstance(request_json, dict)
    assert payload["name"] in request_json["text"]
    assert request_json["chat_id"] == 0


@pytest.mark.asyncio
async def test_send_telegram_message_propagates_http_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "error"})

    transport = httpx.MockTransport(handler)
    ctx = {"http_client": httpx.AsyncClient(transport=transport)}

    payload = {"name": "Err", "email": "err@example.com", "message": "Fails"}

    with pytest.raises(httpx.HTTPStatusError):
        await send_telegram_message(ctx, payload)

    await ctx["http_client"].aclose()
