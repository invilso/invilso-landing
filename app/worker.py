from __future__ import annotations

from app.config import get_settings
from app.workers import registry, worker_shutdown, worker_startup


class WorkerSettings:
    redis_settings = get_settings().redis_settings()
    functions = registry.functions
    on_startup = worker_startup
    on_shutdown = worker_shutdown
    keep_result = 0


__all__ = ["WorkerSettings"]
