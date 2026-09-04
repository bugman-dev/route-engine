from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from orchestrator.api.schemas import (
    TotalDemandOut,
    TotalWaypointsOut,
    WaypointCreate,
    WaypointOut,
    WaypointUpdate,
)
from orchestrator.db import get_db
from orchestrator.db.models import WaypointRow
from orchestrator.db.repositories import WaypointRepository

router = APIRouter(prefix="/waypoints", tags=["waypoints"])


@router.post("", response_model=List[WaypointOut], status_code=201)
def add_waypoints(
    body: Annotated[List[WaypointCreate], Body(min_length=1)],
    db: Session = Depends(get_db),
):
    """Create one or more waypoints from a JSON array."""
    repo = WaypointRepository(db)
    rows = [
        WaypointRow(
            external_id=item.external_id,
            name=item.name,
            latitude=item.latitude,
            longitude=item.longitude,
            demand=item.demand,
            is_depot=item.is_depot,
            is_active=item.is_active,
        )
        for item in body
    ]
    try:
        return list(repo.create_many(rows))
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="One or more waypoints conflict with existing rows (e.g. duplicate external_id).",
        ) from None


@router.get("", response_model=List[WaypointOut])
def get_waypoints(
    active_only: bool = Query(False),
    depot: bool | None = Query(
        None,
        description="If true, only depots; if false, only non-depots; omit for all.",
    ),
    db: Session = Depends(get_db),
):
    return list(
        WaypointRepository(db).list(active_only=active_only, depot=depot)
    )


@router.get("/total", response_model=TotalWaypointsOut)
def get_total_waypoints(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Return the count of waypoints (active by default)."""
    total = WaypointRepository(db).count(active_only=active_only)
    return TotalWaypointsOut(total_waypoints=total, active_only=active_only)


@router.get("/demand/total", response_model=TotalDemandOut)
def get_total_demand(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Return the sum of waypoint demand (active by default)."""
    total = WaypointRepository(db).total_demand(active_only=active_only)
    return TotalDemandOut(total_demand=total, active_only=active_only)


@router.patch("/{waypoint_id}", response_model=WaypointOut)
def update_waypoint(
    waypoint_id: int,
    body: WaypointUpdate,
    db: Session = Depends(get_db),
):
    repo = WaypointRepository(db)
    row = repo.get(waypoint_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Waypoint not found.")

    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(row, key, value)
    return repo.update(row)
