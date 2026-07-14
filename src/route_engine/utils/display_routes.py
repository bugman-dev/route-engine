from route_engine.constants import (
    LABEL_COST,
    LABEL_ETA,
    LABEL_LEGS,
    LABEL_OPERATOR,
    LABEL_STOP_SEPARATOR,
    LABEL_TOTAL_DISTANCE,
    LABEL_TOTAL_DURATION,
    LABEL_VEHICLE,
)


def _format_duration(seconds: int) -> str:
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {secs}s" if secs else f"{minutes}m"
    return f"{secs}s"


def display_routes(formatted_routes):
    """Print routes in a simple human-readable form (CLI helper)."""
    for route in formatted_routes:
        print()
        print(f"{LABEL_VEHICLE}: {route.vehicle_number}")
        print(f"{LABEL_OPERATOR}: {route.operator}")
        print(f"{LABEL_COST}: {route.cost_mode}")
        print(LABEL_STOP_SEPARATOR.join(route.stops))

        # Non-cost metric: ETA when we optimized on distance.
        if route.etas_seconds is not None:
            parts = []
            for stop, eta in zip(route.stops, route.etas_seconds):
                parts.append(f"{stop} (+{_format_duration(eta)})")
            print(f"{LABEL_ETA}: {LABEL_STOP_SEPARATOR.join(parts)}")
            if route.total_duration_seconds is not None:
                print(
                    f"{LABEL_TOTAL_DURATION}: "
                    f"{_format_duration(route.total_duration_seconds)}"
                )

        # Non-cost metric: distance when we optimized on ETA.
        if route.total_distance_km is not None:
            if route.leg_distances_km:
                legs = ", ".join(f"{km} km" for km in route.leg_distances_km)
                print(f"{LABEL_LEGS}: {legs}")
            print(f"{LABEL_TOTAL_DISTANCE}: {route.total_distance_km} km")
