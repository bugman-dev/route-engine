from data import get_waypoints, get_vehicles, get_depot
from utils.display_routes import display_routes
from engine.route_engine import generate_routes

waypoints = get_waypoints()
vehicles = get_vehicles()
depot = get_depot()

routes = generate_routes(waypoints,vehicles,depot)

display_routes(routes)