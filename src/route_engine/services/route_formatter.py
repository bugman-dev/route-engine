from typing import List, Optional

from ..constants import DEFAULT_COST_MODE, CostMode
from ..models.route import Route


def _accumulate_along_path(path, matrix) -> List[int]:
    """Cumulative values at each node (0 at start, then edge sums)."""
    totals = [0]
    for i in range(len(path) - 1):
        totals.append(totals[-1] + matrix[path[i]][path[i + 1]])
    return totals


def _leg_values(path, matrix) -> List[int]:
    """Per-edge values between consecutive nodes."""
    return [matrix[path[i]][path[i + 1]] for i in range(len(path) - 1)]


def format_routes(
    routes,
    waypoints,
    vehicles,
    cost_mode: CostMode = DEFAULT_COST_MODE,
    distance_km=None,
    duration_seconds=None,
) -> List[Route]:
    """
    Map solver node indices to vehicle metadata and stop names.

    When travel matrices are available, annotate each route with both
    distance and duration (OSRM). Haversine has distance only.
    """
    formatted_routes = []

    for vehicle_id, route in enumerate(routes):
        # Depot → depot only means this vehicle was not used.
        if len(route) <= 2:
            continue

        vehicle = vehicles[vehicle_id]
        stops = [waypoints[node].name for node in route]

        etas_seconds: Optional[List[int]] = None
        total_duration_seconds: Optional[int] = None
        leg_distances_km: Optional[List[int]] = None
        total_distance_km: Optional[int] = None

        if distance_km is not None:
            leg_distances_km = _leg_values(route, distance_km)
            total_distance_km = sum(leg_distances_km)

        if duration_seconds is not None:
            etas_seconds = _accumulate_along_path(route, duration_seconds)
            total_duration_seconds = etas_seconds[-1]

        formatted_routes.append(
            Route(
                vehicle_id=vehicle.id,
                vehicle_number=vehicle.number,
                operator=vehicle.operator,
                capacity=vehicle.capacity,
                stops=stops,
                cost_mode=cost_mode,
                etas_seconds=etas_seconds,
                total_duration_seconds=total_duration_seconds,
                leg_distances_km=leg_distances_km,
                total_distance_km=total_distance_km,
            )
        )

    return formatted_routes
