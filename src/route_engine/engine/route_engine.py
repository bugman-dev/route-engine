from ..validators.validator import validate_input_data
from ..services.distance import HaversineDistanceProvider
from .route_optimizer import optimize_routes
from ..services.route_formatter import format_routes


def generate_routes(waypoints, vehicles, depot, distance_provider=None):
    """
    Build capacitated routes for the given fleet and waypoints.

    Args:
        waypoints: Locations to visit. Index `depot` is the start/end node.
        vehicles: Fleet with per-vehicle capacity.
        depot: Index of the depot within `waypoints`.
        distance_provider: Builds the pairwise distance matrix.
            Defaults to straight-line (Haversine) kilometres.
            Pass OsrmDistanceProvider for road-network distances.
    """
    validate_input_data(waypoints, vehicles, depot)

    if distance_provider is None:
        distance_provider = HaversineDistanceProvider()

    distance_matrix = distance_provider.matrix(waypoints)
    optimized_routes = optimize_routes(distance_matrix, vehicles, depot)
    return format_routes(optimized_routes, waypoints, vehicles)
