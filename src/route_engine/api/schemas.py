from typing import List, Optional

from pydantic import BaseModel, Field

from route_engine.constants import CostMode, ProviderName
from route_engine.models.route import Route
from route_engine.models.vehicle import Vehicle
from route_engine.models.waypoint import Waypoint


class GenerateRoutesRequest(BaseModel):
    """Payload for capacitated route generation."""

    waypoints: List[Waypoint] = Field(..., min_length=1)
    vehicles: List[Vehicle] = Field(..., min_length=1)
    depot: int = Field(0, ge=0, description="Index of the depot in waypoints")
    provider: Optional[ProviderName] = Field(
        None,
        description="Travel matrix source; defaults to ROUTE_ENGINE_PROVIDER",
    )
    cost_mode: Optional[CostMode] = Field(
        None,
        description="OR-Tools cost matrix; defaults to ROUTE_ENGINE_COST",
    )


class GenerateRoutesResponse(BaseModel):
    """Optimized routes and the settings that were applied."""

    provider: ProviderName
    cost_mode: CostMode
    routes: List[Route]
