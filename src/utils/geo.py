from math import radians
from math import sin
from math import cos
from math import sqrt
from math import atan2

# Haversine formula
#
# Calculate the distance between two points on the Earth's surface.
#
# Parameters:
# - lat1: Latitude of the first point
# - lon1: Longitude of the first point
# - lat2: Latitude of the second point
# - lon2: Longitude of the second point
#
# Returns:
# - Distance in kilometers
def haversine(lat1, lon1, lat2, lon2):

    earth_radius = 6371

    dlat = radians(lat2 - lat1)

    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return earth_radius * c