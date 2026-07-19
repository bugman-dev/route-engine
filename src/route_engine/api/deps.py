"""Resolve API request options against environment defaults."""

from __future__ import annotations

import os
from typing import Optional, Tuple

from route_engine.constants import (
    COST_MODES,
    DEFAULT_COST_MODE,
    DEFAULT_PROVIDER,
    ENV_COST,
    ENV_PROVIDER,
    PROVIDERS,
    CostMode,
    ProviderName,
)
from route_engine.services.provider_factory import build_distance_provider


def resolve_provider_name(requested: Optional[ProviderName]) -> ProviderName:
    name = requested or os.environ.get(ENV_PROVIDER, DEFAULT_PROVIDER)
    if name not in PROVIDERS:
        raise ValueError(
            f"Invalid provider={name!r}. Expected one of {PROVIDERS}."
        )
    return name  # type: ignore[return-value]


def resolve_cost_mode(requested: Optional[CostMode]) -> CostMode:
    mode = requested or os.environ.get(ENV_COST, DEFAULT_COST_MODE)
    if mode not in COST_MODES:
        raise ValueError(
            f"Invalid cost_mode={mode!r}. Expected one of {COST_MODES}."
        )
    return mode  # type: ignore[return-value]


def resolve_distance_provider(requested: Optional[ProviderName]) -> Tuple[ProviderName, object]:
    name = resolve_provider_name(requested)
    return name, build_distance_provider(name)
