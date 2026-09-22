"""Application settings, loaded from environment variables.

Values come from the process environment first, then a local .env file. The
.env file is never committed - see .env.example for the shape.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HELLO_SERVICE_", env_file=".env", extra="ignore")

    env: Literal["local", "staging", "production"] = "local"
    database_url: str = "sqlite:///./data/hello.sqlite3"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    max_page_size: int = 100


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings. Cached because the DB engine is built once."""
    return Settings()
