from typing import List

from ..models.route import Route


def format_routes(routes, waypoints, vehicles) -> List[Route]:
    """Map solver node indices to vehicle metadata and stop names."""
    formatted_routes = []

    for vehicle_id, route in enumerate(routes):
        # Depot → depot only means this vehicle was not used.
        if len(route) <= 2:
            continue

        vehicle = vehicles[vehicle_id]
        stops = [waypoints[node].name for node in route]

        formatted_routes.append(
            Route(
                vehicle_id=vehicle.id,
                vehicle_number=vehicle.number,
                operator=vehicle.operator,
                capacity=vehicle.capacity,
                stops=stops,
            )
        )

    return formatted_routes
