from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from arq.connections import create_pool
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routers.contact import router as contact_router
from app.routers.pages import router as pages_router

RedisPoolFactory = Callable[[], Awaitable[Any]]


def create_app(redis_pool_factory: RedisPoolFactory | None = None) -> FastAPI:
    """Application factory used by both uvicorn and the test suite."""

    settings = get_settings()
    static_dir = Path(__file__).resolve().parent.parent / "static"

    async def default_redis_pool_factory() -> Any:
        return await create_pool(settings.redis_settings())

    factory: RedisPoolFactory = redis_pool_factory or default_redis_pool_factory

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        redis_pool = await factory()
        app.state.redis = redis_pool
        try:
            yield
        finally:
            close = getattr(redis_pool, "close", None)
            if close is not None:
                maybe_awaitable = close()
                if inspect.isawaitable(maybe_awaitable):
                    await maybe_awaitable

    app = FastAPI(title=settings.project_name, lifespan=lifespan)
    app.include_router(pages_router)
    app.include_router(contact_router, prefix="/api")

    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app
