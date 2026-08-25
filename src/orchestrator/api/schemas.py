"""Pydantic request/response schemas for the orchestrator API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WaypointCreate(BaseModel):
    external_id: Optional[str] = None
    name: str
    latitude: float
    longitude: float
    demand: int = 1
    is_depot: bool = False
    is_active: bool = True


class WaypointUpdate(BaseModel):
    external_id: Optional[str] = None
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    demand: Optional[int] = None
    is_depot: Optional[bool] = None
    is_active: Optional[bool] = None


class WaypointOut(BaseModel):
    id: int
    external_id: Optional[str] = None
    name: str
    latitude: float
    longitude: float
    demand: int
    is_depot: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VehicleCreate(BaseModel):
    external_id: Optional[str] = None
    number: str
    operator: str
    capacity: int = Field(..., gt=0)
    is_active: bool = True


class VehicleUpdate(BaseModel):
    external_id: Optional[str] = None
    number: Optional[str] = None
    operator: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class VehicleOut(BaseModel):
    id: int
    external_id: Optional[str] = None
    number: str
    operator: str
    capacity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TotalWaypointsOut(BaseModel):
    total_waypoints: int
    active_only: bool


class TotalDemandOut(BaseModel):
    total_demand: int
    active_only: bool


class TotalVehiclesOut(BaseModel):
    total_vehicles: int
    active_only: bool


class TotalCapacityOut(BaseModel):
    total_capacity: int
    active_only: bool


class GenerateRoutesBody(BaseModel):
    provider: Optional[str] = None
    cost_mode: Optional[str] = None
    regenerate: bool = False


class RouteGenerationOut(BaseModel):
    cached: bool
    service_date: date | str
    generated_at: datetime | str
    was_regenerated: bool
    provider: str
    cost_mode: str
    routes: List[Dict[str, Any]]
