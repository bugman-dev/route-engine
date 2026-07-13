def display_routes(formatted_routes):
    """Print routes in a simple human-readable form (CLI helper)."""
    for route in formatted_routes:
        print()
        print(f"Vehicle: {route.vehicle_number}")
        print(f"Operator: {route.operator}")
        print(" -> ".join(route.stops))
