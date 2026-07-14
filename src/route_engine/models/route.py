from typing import List, Optional

from pydantic import BaseModel

from route_engine.constants import COST_MODE_DISTANCE, CostMode


class Route(BaseModel):
    """One vehicle's ordered sequence of stops after optimization."""

    vehicle_id: str
    vehicle_number: str
    operator: str
    capacity: int
    stops: List[str]
    # Which matrix OR-Tools minimized for this solve.
    cost_mode: CostMode = COST_MODE_DISTANCE
    # Populated when the non-cost metric is ETA (cost_mode=distance + OSRM).
    etas_seconds: Optional[List[int]] = None
    total_duration_seconds: Optional[int] = None
    # Populated when the non-cost metric is distance (cost_mode=eta + OSRM).
    leg_distances_km: Optional[List[int]] = None
    total_distance_km: Optional[int] = None
