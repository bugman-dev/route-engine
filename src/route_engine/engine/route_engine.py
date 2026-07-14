from ..validators.validator import validate_input_data
from ..services.distance import HaversineDistanceProvider
from ..constants import (
    COST_MODE_DISTANCE,
    COST_MODE_ETA,
    COST_MODES,
    DEFAULT_COST_MODE,
    CostMode,
)
from .route_optimizer import optimize_routes
from ..services.route_formatter import format_routes


def _resolve_cost(matrices, cost_mode: CostMode):
    """
    Pick the OR-Tools cost matrix and the matrix used for display.

    Haversine (no duration) always uses distance and has nothing else to show.
    """
    if matrices.duration_seconds is None:
        return COST_MODE_DISTANCE, matrices.distance_km, None

    if cost_mode == COST_MODE_DISTANCE:
        return COST_MODE_DISTANCE, matrices.distance_km, matrices.duration_seconds

    return COST_MODE_ETA, matrices.duration_seconds, matrices.distance_km


def generate_routes(
    waypoints,
    vehicles,
    depot,
    distance_provider=None,
    cost_mode: CostMode = DEFAULT_COST_MODE,
):
    """
    Build capacitated routes for the given fleet and waypoints.

    Args:
        waypoints: Locations to visit. Index `depot` is the start/end node.
        vehicles: Fleet with per-vehicle capacity.
        depot: Index of the depot within `waypoints`.
        distance_provider: Builds travel matrices (distance, and duration when
            supported). Defaults to Haversine.
        cost_mode: Which matrix OR-Tools minimizes (`distance` or `eta`).
            Ignored when the provider has no duration matrix (Haversine) —
            distance is always used then.
    """
    if cost_mode not in COST_MODES:
        raise ValueError(
            f"Invalid cost_mode={cost_mode!r}. "
            f"Expected one of {COST_MODES}."
        )

    validate_input_data(waypoints, vehicles, depot)

    if distance_provider is None:
        distance_provider = HaversineDistanceProvider()

    matrices = distance_provider.matrix(waypoints)
    resolved_mode, cost_matrix, display_matrix = _resolve_cost(matrices, cost_mode)
    optimized_routes = optimize_routes(cost_matrix, vehicles, depot)
    return format_routes(
        optimized_routes,
        waypoints,
        vehicles,
        cost_mode=resolved_mode,
        display_matrix=display_matrix,
    )
