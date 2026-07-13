from typing import List, Protocol

from ...models.waypoint import Waypoint


class DistanceProvider(Protocol):
    """
    Builds a pairwise distance matrix for a list of waypoints.

    matrix[i][j] is the cost of travelling from waypoints[i] to waypoints[j].
    Implementations may use straight-line distance, road networks, etc.
    """

    def matrix(self, waypoints: List[Waypoint]) -> List[List[int]]:
        ...
