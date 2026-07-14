from typing import List, Protocol

from ...models.waypoint import Waypoint
from .matrices import TravelMatrices


class DistanceProvider(Protocol):
    """
    Builds pairwise travel matrices for a list of waypoints.

    Always includes distance. May also include duration (ETA) when the
    underlying data source supports road travel times.
    """

    def matrix(self, waypoints: List[Waypoint]) -> TravelMatrices:
        ...
