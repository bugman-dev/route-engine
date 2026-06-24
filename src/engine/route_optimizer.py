# Import OR-Tools modules
# pywrapcp -> Core routing solver
# routing_enums_pb2 -> Predefined search strategies
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

def optimize_routes(distance_matrix, cabs, depot):

    num_vehicles = len(cabs)
    # RoutingIndexManager
    #
    # OR-Tools internally uses its own indexing system.
    # The manager translates between:
    #
    # Our node numbers <-> OR-Tools internal indexes
    #
    # Here we are telling OR-Tools:
    #
    # - There are 4 locations
    # - There is 1 cab
    # - All cabs start at Office
    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        num_vehicles,
        depot,
    )

    # Create the routing solver
    #
    # This is the "brain" that will generate routes.
    routing = pywrapcp.RoutingModel(manager)


    # Distance callback
    #
    # OR-Tools repeatedly asks:
    #
    # "If I travel from X to Y, what is the cost?"
    #
    # This function answers that question.
    def distance_callback(from_index, to_index):
        # Convert OR-Tools indexes to our node numbers
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # Return the distance between locations
        return distance_matrix[from_node][to_node]


    # Register our callback with OR-Tools
    #
    # This gives us an identifier that OR-Tools can use.
    transit_callback = routing.RegisterTransitCallback(
        distance_callback
    )

    # Define the optimization objective
    #
    # Minimize the total travel distance for all cabs.
    routing.SetArcCostEvaluatorOfAllVehicles(
        transit_callback
    )

    # Configure how OR-Tools searches for a solution
    search_parameters = (
        pywrapcp.DefaultRoutingSearchParameters()
    )

    # PATH_CHEAPEST_ARC means:
    #
    # At each step, choose the cheapest next location.
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Ask OR-Tools to generate a route
    solution = routing.SolveWithParameters(
        search_parameters
    )

    # If a valid route was found
    if solution:
        routes = []

        for vehicle_id in range(num_vehicles):
            # Start from vehicle 0
            index = routing.Start(vehicle_id)
            route = []

            # Traverse the route until we reach the end
            while not routing.IsEnd(index):

                # Convert OR-Tools index to our node number
                route.append(
                    manager.IndexToNode(index)
                )

                # Move to the next location
                index = solution.Value(
                    routing.NextVar(index)
                )

            # Add the final location
            route.append(
                manager.IndexToNode(index)
            )
            routes.append(route)

        return(routes)

