from pydantic import BaseModel


class Vehicle(BaseModel):
    """A vehicle in the fleet that can serve demand stops."""

    id: str
    number: str
    operator: str
    capacity: int
