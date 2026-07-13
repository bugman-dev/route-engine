from pydantic import BaseModel


class Waypoint(BaseModel):
    """A location in the routing problem (depot or demand stop)."""

    id: str
    name: str
    latitude: float
    longitude: float
    # Units of capacity consumed at this stop (depot is typically 0).
    demand: int = 1
