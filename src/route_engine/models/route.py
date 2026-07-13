from typing import List

from pydantic import BaseModel


class Route(BaseModel):
    """One vehicle's ordered sequence of stops after optimization."""

    vehicle_id: str
    vehicle_number: str
    operator: str
    capacity: int
    stops: List[str]
