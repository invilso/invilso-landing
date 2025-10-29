from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Dict, List

JobCallable = Callable[[Dict[str, Any], Dict[str, Any]], Awaitable[None]]
LifecycleHook = Callable[[Dict[str, Any]], Awaitable[None]]


class JobRegistry:
    """Lightweight registry for ARQ jobs and lifecycle hooks."""

    def __init__(self) -> None:
        self._jobs: Dict[str, JobCallable] = {}
        self._startup: List[LifecycleHook] = []
        self._shutdown: List[LifecycleHook] = []

    def job(self, name: str | None = None) -> Callable[[JobCallable], JobCallable]:
        def decorator(func: JobCallable) -> JobCallable:
            job_name = name or func.__name__
            if job_name in self._jobs:
                raise ValueError(f"Job '{job_name}' already registered.")
            self._jobs[job_name] = func
            return func

        return decorator

    def on_startup(self, func: LifecycleHook) -> LifecycleHook:
        self._startup.append(func)
        return func

    def on_shutdown(self, func: LifecycleHook) -> LifecycleHook:
        self._shutdown.append(func)
        return func

    def job_name(self, func: JobCallable) -> str:
        for name, handler in self._jobs.items():
            if handler is func:
                return name
        raise KeyError("Function not registered as a job.")

    @property
    def functions(self) -> List[JobCallable]:
        return list(self._jobs.values())

    async def run_startup(self, ctx: Dict[str, Any]) -> None:
        for hook in self._startup:
            await hook(ctx)

    async def run_shutdown(self, ctx: Dict[str, Any]) -> None:
        for hook in reversed(self._shutdown):
            await hook(ctx)


registry = JobRegistry()

__all__ = ["registry", "JobRegistry", "JobCallable"]
