def validate_capacity(waypoints, vehicles):
    employee_count = len(waypoints) - 1
    total_capacity = sum(
        vehicle.capacity
        for vehicle in vehicles
    )

    if total_capacity < employee_count:
        raise ValueError(
            f"Not enough seats. "
            f"Employees={employee_count}, "
            f"Capacity={total_capacity}"
        )