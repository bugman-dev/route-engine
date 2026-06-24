

from data import get_locations, get_cabs, get_depot
from services.distance_matrix import generate_distance_matrix
from engine.route_optimizer import optimize_routes
from services.route_formatter import create_readable_route

locations = get_locations()
cabs = get_cabs()
depot = get_depot()

distance_matrix = generate_distance_matrix(locations)

optimized_routes = optimize_routes(distance_matrix, len(cabs), depot)

redeable_route = create_readable_route(optimized_routes, locations, cabs)

print(redeable_route)