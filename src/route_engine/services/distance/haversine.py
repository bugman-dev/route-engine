from typing import List

from ...models.waypoint import Waypoint
from ...utils.geo import haversine
from .matrices import TravelMatrices


class HaversineDistanceProvider:
    """Straight-line distance in kilometres (no duration / ETA matrix)."""

    def matrix(self, waypoints: List[Waypoint]) -> TravelMatrices:
        rows = []
        for origin in waypoints:
            row = [
                round(
                    haversine(
                        origin.latitude,
                        origin.longitude,
                        destination.latitude,
                        destination.longitude,
                    )
                )
                for destination in waypoints
            ]
            rows.append(row)
        return TravelMatrices(distance_km=rows, duration_seconds=None)
