from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from app.config import get_settings
from app.workers import registry


def _format_message(payload: Mapping[str, Any]) -> str:
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip()
    message = str(payload.get("message", "")).strip()

    return (
        "New contact request received:\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        "Message:\n"
        f"{message}"
    )


@registry.on_startup
async def worker_startup(ctx: dict[str, Any]) -> None:
    """Initialise shared resources for the worker."""
    settings = get_settings()
    ctx["http_client"] = httpx.AsyncClient(timeout=httpx.Timeout(settings.request_timeout_seconds))


@registry.on_shutdown
async def worker_shutdown(ctx: dict[str, Any]) -> None:
    """Tear down shared worker resources."""
    client: httpx.AsyncClient | None = ctx.pop("http_client", None)
    if client is not None:
        await client.aclose()


@registry.job()
async def send_telegram_message(ctx: dict[str, Any], payload: Mapping[str, Any]) -> None:
    """Dispatch the formatted message to the configured Telegram chat."""
    settings = get_settings()
    message_text = _format_message(payload)
    client: httpx.AsyncClient = ctx["http_client"]

    response = await client.post(
        settings.telegram_api_url,
        json={
            "chat_id": settings.telegram_chat_id,
            "text": message_text,
            "disable_web_page_preview": True,
        },
    )
    response.raise_for_status()


__all__ = [
    "worker_startup",
    "worker_shutdown",
    "send_telegram_message",
]
