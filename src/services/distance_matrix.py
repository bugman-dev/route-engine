from utils.geo import haversine

def generate_distance_matrix(locations):
    matrix = []
    for origin in locations:
        row = []
        for destination in locations:
            distance = haversine(
                origin["latitude"],
                origin["longitude"],
                destination["latitude"],
                destination["longitude"],
            )
            row.append(
                round(distance)
            )
        matrix.append(row)
    return matrix