from typing import List
from ..models.route import Route

def format_routes(routes, waypoints, vehicles) -> List[Route]:
    formatted_routes = []
    for vehicle_id, route in enumerate(routes):
        # Skip unused vehicles
        if len(route) <= 2:
            continue

        vehicle = vehicles[vehicle_id]
        stops = []

        for node in route:
            stops.append(
                waypoints[node].name
            )

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