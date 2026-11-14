from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "Blog API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = Field(default="dev-only-change-me-before-deployment", min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, gt=0)
    DATABASE_URL: str = "sqlite+aiosqlite:///./blog.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CONNECT_TIMEOUT: float = Field(default=1.0, gt=0)
    CACHE_TTL: int = Field(default=300, gt=0)
    VIEWS_FLUSH_THRESHOLD: int = Field(default=100, gt=0)
    LOGIN_RATE_LIMIT: int = Field(default=5, gt=0)
    LOGIN_RATE_WINDOW_SECONDS: int = Field(default=60, gt=0)
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "testserver", "blog.example.com"]
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://blog.example.com"]

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
