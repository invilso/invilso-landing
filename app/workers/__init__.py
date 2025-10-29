from __future__ import annotations

from app.workers.registry import registry

# Import job modules so that they self-register on import
from app.services import telegram as _telegram  # noqa: F401


async def worker_startup(ctx: dict[str, object]) -> None:
    await registry.run_startup(ctx)  # type: ignore[arg-type]


async def worker_shutdown(ctx: dict[str, object]) -> None:
    await registry.run_shutdown(ctx)  # type: ignore[arg-type]


__all__ = ["registry", "worker_startup", "worker_shutdown"]
