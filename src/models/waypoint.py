from pydantic import BaseModel

class Waypoint(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    demand: int = 1