

from data import get_locations, get_num_vehicles, get_depot
from services.distance_matrix import generate_distance_matrix
from engine.route_optimizer import optimize_routes
from services.route_formatter import create_readable_route

locations = get_locations()
num_vehicles = get_num_vehicles()
depot = get_depot()

distance_matrix = generate_distance_matrix(locations)

optimized_routes = optimize_routes(distance_matrix, num_vehicles, depot)

redeable_route = create_readable_route(optimized_routes, locations)

print(redeable_route)