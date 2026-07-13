def validate_capacity(waypoints, vehicles):
    """Ensure the fleet can carry total demand (all non-depot stops)."""
    # One depot + N demand stops; matches the solver's demand vector.
    demand_count = len(waypoints) - 1
    total_capacity = sum(vehicle.capacity for vehicle in vehicles)

    if total_capacity < demand_count:
        raise ValueError(
            f"Not enough capacity. "
            f"Demand={demand_count}, "
            f"Capacity={total_capacity}"
        )
