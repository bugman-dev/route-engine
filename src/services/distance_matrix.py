from utils.geo import haversine

def generate_distance_matrix(waypoints):
    matrix = []
    for origin in waypoints:
        row = []
        for destination in waypoints:
            distance = haversine(
                origin.latitude,
                origin.longitude,
                destination.latitude,
                destination.longitude,
            )
            row.append(
                round(distance)
            )
        matrix.append(row)
    return matrix