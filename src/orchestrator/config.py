"""Orchestrator configuration from environment."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

from orchestrator.constants import (
    DEFAULT_DATABASE_URL,
    DEFAULT_ENGINE_BASE_URL,
    DEFAULT_ENGINE_TIMEOUT_SECONDS,
    DEFAULT_HEALTH_TIMEOUT_SECONDS,
    DEFAULT_OSRM_BASE_URL,
    DEFAULT_TIMEZONE,
    ENV_DATABASE_URL,
    ENV_ENGINE_BASE_URL,
    ENV_ENGINE_TIMEOUT,
    ENV_HEALTH_TIMEOUT,
    ENV_ORCHESTRATOR_TZ,
    ENV_OSRM_BASE_URL,
)

# src/orchestrator/config.py -> project root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_env() -> None:
    load_dotenv(_PROJECT_ROOT / ".env", override=False)


@lru_cache
def get_settings() -> "Settings":
    load_env()
    return Settings()


class Settings:
    def __init__(self) -> None:
        self.database_url = os.environ.get(ENV_DATABASE_URL, DEFAULT_DATABASE_URL)
        self.engine_base_url = os.environ.get(
            ENV_ENGINE_BASE_URL, DEFAULT_ENGINE_BASE_URL
        ).rstrip("/")
        self.osrm_base_url = os.environ.get(
            ENV_OSRM_BASE_URL, DEFAULT_OSRM_BASE_URL
        ).rstrip("/")
        self.timezone = os.environ.get(ENV_ORCHESTRATOR_TZ, DEFAULT_TIMEZONE)
        timeout_raw = os.environ.get(
            ENV_ENGINE_TIMEOUT, str(DEFAULT_ENGINE_TIMEOUT_SECONDS)
        )
        self.engine_timeout_seconds = float(timeout_raw)
        health_timeout_raw = os.environ.get(
            ENV_HEALTH_TIMEOUT, str(DEFAULT_HEALTH_TIMEOUT_SECONDS)
        )
        self.health_timeout_seconds = float(health_timeout_raw)
