"""OR-Tools capacitated vehicle routing (CVRP) solver."""

from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2


def optimize_routes(distance_matrix, vehicles, depot):
    """
    Assign stops to vehicles and order them to minimize total distance.

    Returns a list of routes (one per vehicle). Each route is a list of
    waypoint indices starting and ending at the depot. Unused vehicles
    return a depot-only path (length 2), which the formatter drops.
    """
    num_vehicles = len(vehicles)
    vehicle_capacities = [vehicle.capacity for vehicle in vehicles]

    # Maps our node indices <-> OR-Tools internal indices.
    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        num_vehicles,
        depot,
    )
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback = routing.RegisterTransitCallback(distance_callback)
    # Objective: minimize total travel distance across the fleet.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback)

    # Depot has zero demand; every other stop consumes 1 unit of capacity.
    # Later this can read Waypoint.demand instead of assuming 1.
    demands = [0] + [1] * (len(distance_matrix) - 1)

    def demand_callback(from_index):
        return demands[manager.IndexToNode(from_index)]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        vehicle_capacities,
        True,
        "Capacity",
    )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    # Greedy construction: at each step, pick the cheapest next stop.
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_parameters)
    if not solution:
        raise ValueError("No feasible routes found for the given inputs.")

    routes = []
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))
        routes.append(route)

    return routes
