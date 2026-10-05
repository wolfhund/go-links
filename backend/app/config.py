"""Application settings, read once from environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the Go Links service."""

    database_url: str = "sqlite:///./golinks.db"
    frontend_url: str = "http://localhost:5173"
    log_level: str = "INFO"


def load_settings() -> Settings:
    """Build settings from environment variables, falling back to defaults."""
    defaults = Settings()
    return Settings(
        database_url=os.getenv("GOLINKS_DATABASE_URL", defaults.database_url),
        frontend_url=os.getenv("GOLINKS_FRONTEND_URL", defaults.frontend_url),
        log_level=os.getenv("GOLINKS_LOG_LEVEL", defaults.log_level),
    )
