"""CLI entrypoint — loads sample data and prints optimized routes."""

import argparse
import os

from route_engine.config import load_env
from route_engine.examples.sample_data import get_depot, get_vehicles, get_waypoints
from route_engine.engine.route_engine import generate_routes
from route_engine.services.distance import (
    HaversineDistanceProvider,
    OsrmDistanceProvider,
)
from route_engine.utils.display_routes import display_routes

load_env()


def _build_distance_provider(name: str):
    if name == "haversine":
        return HaversineDistanceProvider()
    if name == "osrm":
        base_url = os.environ.get(
            "OSRM_BASE_URL",
            "https://router.project-osrm.org",
        )
        return OsrmDistanceProvider(base_url=base_url)
    raise ValueError(f"Unknown distance provider: {name}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate capacitated vehicle routes for the sample dataset.",
    )
    parser.add_argument(
        "--provider",
        choices=("haversine", "osrm"),
        default=os.environ.get("ROUTE_ENGINE_PROVIDER", "haversine"),
        help="Distance matrix source (default from .env / ROUTE_ENGINE_PROVIDER). "
        "Use osrm for road-network distances.",
    )
    args = parser.parse_args(argv)

    waypoints = get_waypoints()
    vehicles = get_vehicles()
    depot = get_depot()
    distance_provider = _build_distance_provider(args.provider)

    routes = generate_routes(
        waypoints,
        vehicles,
        depot,
        distance_provider=distance_provider,
    )
    display_routes(routes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
