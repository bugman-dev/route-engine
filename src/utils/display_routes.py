def display_routes(formatted_routes):
    # Print output
    for route in formatted_routes:

        print()

        print(
            f"Cab: {route.vehicle_number}"
        )

        print(
            f"Driver: {route.operator}"
        )

        print(
            " -> ".join(
                route.stops
            )
        )