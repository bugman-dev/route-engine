def create_readable_route(optimized_routes, locations, cabs):
    lines = []
    for (vehicle_id, route) in enumerate(optimized_routes):
        readable_route = [locations[node]["name"] for node in route]
        route_line = " -> ".join(readable_route)
        cab_number = cabs[vehicle_id]["vehicleNumber"]

        lines.append(f"Cab {cab_number}:\n{route_line}")

    
    return "\n\n".join(lines)