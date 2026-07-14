from typing import List, Optional

from pydantic import BaseModel


class TravelMatrices(BaseModel):
    """Paired travel costs between waypoints.

    distance_km is always present. duration_seconds is set by road-network
    providers (e.g. OSRM) and is None for Haversine.
    """

    distance_km: List[List[int]]
    duration_seconds: Optional[List[List[int]]] = None
