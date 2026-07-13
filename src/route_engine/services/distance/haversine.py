from typing import List

from ...models.waypoint import Waypoint
from ...utils.geo import haversine


class HaversineDistanceProvider:
    """Straight-line distance in kilometres (rounded to int for OR-Tools)."""

    def matrix(self, waypoints: List[Waypoint]) -> List[List[int]]:
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
        return rows
