from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from orchestrator.api.schemas import (
    TotalCapacityOut,
    VehicleCreate,
    VehicleOut,
    VehicleUpdate,
)
from orchestrator.db import get_db
from orchestrator.db.models import VehicleRow
from orchestrator.db.repositories import VehicleRepository

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("", response_model=List[VehicleOut], status_code=201)
def add_vehicles(
    body: Annotated[List[VehicleCreate], Body(min_length=1)],
    db: Session = Depends(get_db),
):
    """Create one or more vehicles from a JSON array."""
    repo = VehicleRepository(db)
    rows = [
        VehicleRow(
            external_id=item.external_id,
            number=item.number,
            operator=item.operator,
            capacity=item.capacity,
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
            detail="One or more vehicles conflict with existing rows (e.g. duplicate external_id).",
        ) from None


@router.get("", response_model=List[VehicleOut])
def get_vehicles(
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    return list(VehicleRepository(db).list(active_only=active_only))


@router.get("/capacity/total", response_model=TotalCapacityOut)
def get_total_capacity(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Return the sum of vehicle capacity (active by default)."""
    total = VehicleRepository(db).total_capacity(active_only=active_only)
    return TotalCapacityOut(total_capacity=total, active_only=active_only)


@router.patch("/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(
    vehicle_id: int,
    body: VehicleUpdate,
    db: Session = Depends(get_db),
):
    repo = VehicleRepository(db)
    row = repo.get(vehicle_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Vehicle not found.")

    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(row, key, value)
    return repo.update(row)
