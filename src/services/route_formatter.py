def create_readable_route(optimized_routes, locations):
    return [locations[node]["name"] for node in optimized_routes]