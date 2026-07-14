"""CLI entrypoint — loads sample data and prints optimized routes."""

import argparse
import os

from route_engine.config import load_env
from route_engine.constants import (
    COST_MODES,
    DEFAULT_COST_MODE,
    DEFAULT_OSRM_BASE_URL,
    DEFAULT_PROVIDER,
    ENV_COST,
    ENV_OSRM_BASE_URL,
    ENV_PROVIDER,
    PROVIDER_HAVERSINE,
    PROVIDER_OSRM,
    PROVIDERS,
)
from route_engine.examples.sample_data import get_depot, get_vehicles, get_waypoints
from route_engine.engine.route_engine import generate_routes
from route_engine.services.distance import (
    HaversineDistanceProvider,
    OsrmDistanceProvider,
)
from route_engine.utils.display_routes import display_routes

load_env()


def _build_distance_provider(name: str):
    if name == PROVIDER_HAVERSINE:
        return HaversineDistanceProvider()
    if name == PROVIDER_OSRM:
        base_url = os.environ.get(ENV_OSRM_BASE_URL, DEFAULT_OSRM_BASE_URL)
        return OsrmDistanceProvider(base_url=base_url)
    raise ValueError(f"Unknown distance provider: {name}")


def _resolve_cost_mode(value: str) -> str:
    if value not in COST_MODES:
        raise ValueError(
            f"Invalid {ENV_COST}={value!r}. "
            f"Expected one of {COST_MODES}."
        )
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate capacitated vehicle routes for the sample dataset.",
    )
    parser.add_argument(
        "--provider",
        choices=PROVIDERS,
        default=os.environ.get(ENV_PROVIDER, DEFAULT_PROVIDER),
        help=f"Distance matrix source (default from .env / {ENV_PROVIDER}). "
        "Use osrm for road-network distances and ETAs.",
    )
    parser.add_argument(
        "--cost",
        choices=COST_MODES,
        default=None,
        help="OR-Tools cost matrix: distance or eta "
        f"(default from .env / {ENV_COST}). "
        "Ignored when provider is haversine.",
    )
    args = parser.parse_args(argv)

    cost_mode = _resolve_cost_mode(
        args.cost
        if args.cost is not None
        else os.environ.get(ENV_COST, DEFAULT_COST_MODE)
    )

    waypoints = get_waypoints()
    vehicles = get_vehicles()
    depot = get_depot()
    distance_provider = _build_distance_provider(args.provider)

    routes = generate_routes(
        waypoints,
        vehicles,
        depot,
        distance_provider=distance_provider,
        cost_mode=cost_mode,
    )
    display_routes(routes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
