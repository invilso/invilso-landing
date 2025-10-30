from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Optional

from fastapi import HTTPException, Request, status
from limits import RateLimitItem
from limits.aio.storage import MemoryStorage, RedisStorage, Storage  # type: ignore[attr-defined]
from limits.aio.strategies import FixedWindowRateLimiter  # type: ignore[attr-defined]

from app.config import get_settings

Identifier = Callable[[Request], str]
DependencyCallable = Callable[[Request], Awaitable[None]]


class RateLimitService:
    def __init__(self, storage: Storage):
        self._storage = storage
        self._strategy = FixedWindowRateLimiter(storage)

    @property
    def storage(self) -> Storage:
        return self._storage

    def set_storage(self, storage: Storage) -> None:
        self._storage = storage
        self._strategy = FixedWindowRateLimiter(storage)

    async def hit(self, item: RateLimitItem, namespace: str, key: str) -> bool:
        return await self._strategy.hit(item, namespace, key)


_rate_limit_service: RateLimitService | None = None
_rate_limit_service_lock = asyncio.Lock()


def _build_redis_storage() -> Storage:
    settings = get_settings()
    password = getattr(settings, "redis_password", None) or ""
    credentials = f":{password}@" if password else ""
    uri = f"redis://{credentials}{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
    return RedisStorage(uri)


async def get_rate_limit_service() -> RateLimitService:
    global _rate_limit_service
    if _rate_limit_service is not None:
        return _rate_limit_service

    async with _rate_limit_service_lock:
        if _rate_limit_service is None:
            _rate_limit_service = RateLimitService(_build_redis_storage())

    return _rate_limit_service


def reset_rate_limit_service(storage: Optional[Storage] = None) -> None:
    global _rate_limit_service
    if storage is None:
        storage = MemoryStorage()
    if _rate_limit_service is None:
        _rate_limit_service = RateLimitService(storage)
    else:
        _rate_limit_service.set_storage(storage)


def resolve_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()

    client = request.client
    if client and client.host:
        return client.host

    return "unknown"


def rate_limit(
    item: RateLimitItem,
    namespace: str = "default",
    identifier: Identifier | None = None,
    detail: str | None = None,
) -> DependencyCallable:
    resolved_identifier = identifier or resolve_client_ip
    error_detail = detail or "Too many requests."

    async def dependency(request: Request) -> None:
        service = await get_rate_limit_service()
        key = resolved_identifier(request)
        allowed = await service.hit(item, namespace, key)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_detail,
            )

    return dependency


def rate_limit_by_ip(
    item: RateLimitItem,
    namespace: str = "default",
    detail: str | None = None,
) -> DependencyCallable:
    return rate_limit(
        item=item,
        namespace=namespace,
        identifier=resolve_client_ip,
        detail=detail,
    )