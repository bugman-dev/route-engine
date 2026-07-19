"""Build distance providers from configuration names."""

import os

from route_engine.constants import (
    DEFAULT_OSRM_BASE_URL,
    ENV_OSRM_BASE_URL,
    PROVIDER_HAVERSINE,
    PROVIDER_OSRM,
)
from route_engine.services.distance import (
    HaversineDistanceProvider,
    OsrmDistanceProvider,
)


def build_distance_provider(name: str):
    """Return a distance provider for the given name (`haversine` or `osrm`)."""
    if name == PROVIDER_HAVERSINE:
        return HaversineDistanceProvider()
    if name == PROVIDER_OSRM:
        base_url = os.environ.get(ENV_OSRM_BASE_URL, DEFAULT_OSRM_BASE_URL)
        return OsrmDistanceProvider(base_url=base_url)
    raise ValueError(f"Unknown distance provider: {name}")
