from .capacity_validator import validate_capacity


def validate_input_data(waypoints, vehicles, depot):
    """Run all input checks before solving."""
    if not 0 <= depot < len(waypoints):
        raise ValueError(
            f"Depot index {depot} is out of range "
            f"for {len(waypoints)} waypoints."
        )
    validate_capacity(waypoints, vehicles)

