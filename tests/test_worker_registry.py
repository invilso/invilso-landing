from __future__ import annotations

from typing import Any

import pytest

from app.workers.registry import JobRegistry


@pytest.mark.asyncio
async def test_job_registry_registers_jobs_and_hooks() -> None:
    registry = JobRegistry()
    events: list[str] = []

    @registry.on_startup
    async def startup(ctx: dict[str, Any]) -> None:
        ctx["value"] = 1
        events.append("startup")

    @registry.on_shutdown
    async def shutdown(ctx: dict[str, Any]) -> None:
        events.append("shutdown")

    @registry.job()
    async def sample(ctx: dict[str, Any], payload: dict[str, Any]) -> None:
        ctx["value"] = payload["value"]

    assert registry.job_name(sample) == "sample"
    assert registry.functions == [sample]

    context: dict[str, Any] = {}
    await registry.run_startup(context)
    assert context["value"] == 1

    await sample(context, {"value": 2})
    assert context["value"] == 2

    await registry.run_shutdown(context)
    assert events == ["startup", "shutdown"]


def test_job_registry_duplicate_registration_raises() -> None:
    registry = JobRegistry()

    @registry.job(name="duplicate")
    async def _first(ctx: dict[str, Any], payload: dict[str, Any]) -> None:  # pragma: no cover - body unused
        return None

    with pytest.raises(ValueError):
        @registry.job(name="duplicate")
        async def _second(ctx: dict[str, Any], payload: dict[str, Any]) -> None:  # pragma: no cover - body unused
            return None


def test_job_registry_job_name_errors_for_unknown_function() -> None:
    registry = JobRegistry()

    async def dummy(ctx: dict[str, Any], payload: dict[str, Any]) -> None:  # pragma: no cover - body unused
        return None

    with pytest.raises(KeyError):
        registry.job_name(dummy)
