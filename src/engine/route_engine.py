from ..validators.validator import validate_input_data
from ..services.distance_matrix import generate_distance_matrix
from .route_optimizer import optimize_routes
from ..services.route_formatter import format_routes

def generate_routes(waypoints, vehicles, depot):
    validate_input_data(waypoints, vehicles, depot)

    distance_matrix = generate_distance_matrix(waypoints)
    optimized_routes = optimize_routes(distance_matrix, vehicles, depot)
    formatted_routes = format_routes(optimized_routes, waypoints, vehicles)

    return formatted_routes