"""Database access helpers."""

from __future__ import annotations

from datetime import date
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from orchestrator.db.models import RouteGenerationRow, VehicleRow, WaypointRow


class WaypointRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, row: WaypointRow) -> WaypointRow:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def create_many(self, rows: Sequence[WaypointRow]) -> Sequence[WaypointRow]:
        self.db.add_all(list(rows))
        self.db.commit()
        for row in rows:
            self.db.refresh(row)
        return rows

    def get(self, waypoint_id: int) -> Optional[WaypointRow]:
        return self.db.get(WaypointRow, waypoint_id)

    def list(self, active_only: bool = False) -> Sequence[WaypointRow]:
        stmt = select(WaypointRow).order_by(WaypointRow.id)
        if active_only:
            stmt = stmt.where(WaypointRow.is_active.is_(True))
        return self.db.scalars(stmt).all()

    def count(self, active_only: bool = True) -> int:
        stmt = select(func.count()).select_from(WaypointRow)
        if active_only:
            stmt = stmt.where(WaypointRow.is_active.is_(True))
        return int(self.db.scalar(stmt) or 0)

    def total_demand(self, active_only: bool = True) -> int:
        stmt = select(func.coalesce(func.sum(WaypointRow.demand), 0))
        if active_only:
            stmt = stmt.where(WaypointRow.is_active.is_(True))
        return int(self.db.scalar(stmt) or 0)

    def update(self, row: WaypointRow) -> WaypointRow:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row


class VehicleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, row: VehicleRow) -> VehicleRow:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def create_many(self, rows: Sequence[VehicleRow]) -> Sequence[VehicleRow]:
        self.db.add_all(list(rows))
        self.db.commit()
        for row in rows:
            self.db.refresh(row)
        return rows

    def get(self, vehicle_id: int) -> Optional[VehicleRow]:
        return self.db.get(VehicleRow, vehicle_id)

    def list(self, active_only: bool = False) -> Sequence[VehicleRow]:
        stmt = select(VehicleRow).order_by(VehicleRow.id)
        if active_only:
            stmt = stmt.where(VehicleRow.is_active.is_(True))
        return self.db.scalars(stmt).all()

    def count(self, active_only: bool = True) -> int:
        stmt = select(func.count()).select_from(VehicleRow)
        if active_only:
            stmt = stmt.where(VehicleRow.is_active.is_(True))
        return int(self.db.scalar(stmt) or 0)

    def total_capacity(self, active_only: bool = True) -> int:
        stmt = select(func.coalesce(func.sum(VehicleRow.capacity), 0))
        if active_only:
            stmt = stmt.where(VehicleRow.is_active.is_(True))
        return int(self.db.scalar(stmt) or 0)

    def update(self, row: VehicleRow) -> VehicleRow:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row


class RouteGenerationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def latest_for_date(self, service_date: date) -> Optional[RouteGenerationRow]:
        stmt = (
            select(RouteGenerationRow)
            .where(RouteGenerationRow.service_date == service_date)
            .order_by(RouteGenerationRow.generated_at.desc())
            .limit(1)
        )
        return self.db.scalars(stmt).first()

    def create(self, row: RouteGenerationRow) -> RouteGenerationRow:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
