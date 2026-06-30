from pydantic import BaseModel

class Vehicle(BaseModel):
    id: str
    number: str
    operator: str
    capacity: int