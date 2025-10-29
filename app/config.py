from __future__ import annotations

from functools import lru_cache

from arq.connections import RedisSettings
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration sourced from environment variables."""

    project_name: str = Field("invilso-landing", alias="PROJECT_NAME")
    telegram_bot_token: str = Field("test-token", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: int = Field(0, alias="TELEGRAM_CHAT_ID")
    redis_host: str = Field("redis", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_db: int = Field(0, alias="REDIS_DB")
    redis_password: str | None = Field(None, alias="REDIS_PASSWORD")
    request_timeout_seconds: float = Field(10.0, alias="REQUEST_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def telegram_api_url(self) -> str:
        return f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"

    def redis_settings(self) -> RedisSettings:
        return RedisSettings(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            database=self.redis_db,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings() # type: ignore[call-arg]


__all__ = ["Settings", "get_settings"]
