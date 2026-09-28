from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-only configuration; secrets are never committed."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local", pattern="^(local|staging|production)$")
    app_name: str = "HMC AI Support Platform"
    app_secret_key: SecretStr
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    cors_origins: str = "http://localhost:3000"
    database_url: str
    database_url_sync: str
    redis_url: str
    owner_bootstrap_email: str | None = None
    owner_bootstrap_password: SecretStr | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
