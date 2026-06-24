def display_routes(formatted_routes):
    # Print output
    for route in formatted_routes:

        print()

        print(
            f"Cab: {route['vehicleNumber']}"
        )

        print(
            f"Driver: {route['driver']}"
        )

        print(
            " -> ".join(
                route["stops"]
            )
        )