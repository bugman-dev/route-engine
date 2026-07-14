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
        print(f"Vehicle: {route.vehicle_number}")
        print(f"Operator: {route.operator}")
        print(f"Cost: {route.cost_mode}")
        print(" -> ".join(route.stops))

        # Non-cost metric: ETA when we optimized on distance.
        if route.etas_seconds is not None:
            parts = []
            for stop, eta in zip(route.stops, route.etas_seconds):
                parts.append(f"{stop} (+{_format_duration(eta)})")
            print("ETA: " + " -> ".join(parts))
            if route.total_duration_seconds is not None:
                print(
                    f"Total duration: {_format_duration(route.total_duration_seconds)}"
                )

        # Non-cost metric: distance when we optimized on ETA.
        if route.total_distance_km is not None:
            if route.leg_distances_km:
                legs = ", ".join(f"{km} km" for km in route.leg_distances_km)
                print(f"Legs: {legs}")
            print(f"Total distance: {route.total_distance_km} km")
