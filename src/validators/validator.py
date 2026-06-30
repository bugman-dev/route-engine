from .capacity_validator import validate_capacity

def validate_input_data(waypoints, vehicles, depot):
    validate_capacity(waypoints, vehicles)