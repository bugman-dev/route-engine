"""Route generation orchestration: DB fleet + engine HTTP + same-day cache."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from orchestrator.config import Settings, get_settings
from orchestrator.db.models import RouteGenerationRow, VehicleRow, WaypointRow
from orchestrator.db.repositories import (
    RouteGenerationRepository,
    VehicleRepository,
    WaypointRepository,
)
from orchestrator.services.engine_client import EngineClient


class RouteServiceError(Exception):
    """Domain / validation error in the orchestrator."""


def service_date_now(settings: Optional[Settings] = None) -> date:
    settings = settings or get_settings()
    return datetime.now(ZoneInfo(settings.timezone)).date()


def now_naive_local(settings: Optional[Settings] = None) -> datetime:
    """Wall-clock time in orchestrator timezone, stored as naive datetime."""
    settings = settings or get_settings()
    return datetime.now(ZoneInfo(settings.timezone)).replace(tzinfo=None)


def build_engine_payload(
    waypoints: List[WaypointRow],
    vehicles: List[VehicleRow],
    provider: Optional[str] = None,
    cost_mode: Optional[str] = None,
) -> Dict[str, Any]:
    if not waypoints:
        raise RouteServiceError("No active waypoints available.")
    if not vehicles:
        raise RouteServiceError("No active vehicles available.")

    depots = [wp for wp in waypoints if wp.is_depot]
    if len(depots) == 0:
        raise RouteServiceError(
            "Exactly one active depot waypoint is required (is_depot=true)."
        )
    if len(depots) > 1:
        raise RouteServiceError(
            "Multiple active depot waypoints found; keep only one is_depot=true."
        )

    depot = depots[0]
    ordered = [depot] + [wp for wp in waypoints if wp.id != depot.id]

    engine_waypoints = [
        {
            "id": wp.external_id or str(wp.id),
            "name": wp.name,
            "latitude": wp.latitude,
            "longitude": wp.longitude,
            "demand": wp.demand,
        }
        for wp in ordered
    ]
    engine_vehicles = [
        {
            "id": vh.external_id or str(vh.id),
            "number": vh.number,
            "operator": vh.operator,
            "capacity": vh.capacity,
        }
        for vh in vehicles
    ]

    payload: Dict[str, Any] = {
        "waypoints": engine_waypoints,
        "vehicles": engine_vehicles,
        "depot": 0,
    }
    if provider is not None:
        payload["provider"] = provider
    if cost_mode is not None:
        payload["cost_mode"] = cost_mode
    return payload


def generation_to_response(
    row: RouteGenerationRow, *, cached: bool
) -> Dict[str, Any]:
    engine = row.engine_response_json or {}
    return {
        "cached": cached,
        "service_date": row.service_date.isoformat(),
        "generated_at": row.generated_at.isoformat(sep=" ", timespec="seconds"),
        "was_regenerated": row.was_regenerated,
        "provider": engine.get("provider", row.provider),
        "cost_mode": engine.get("cost_mode", row.cost_mode),
        "routes": engine.get("routes", []),
    }


class RouteService:
    def __init__(
        self,
        db: Session,
        engine_client: Optional[EngineClient] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.engine_client = engine_client or EngineClient(self.settings)
        self.waypoints = WaypointRepository(db)
        self.vehicles = VehicleRepository(db)
        self.generations = RouteGenerationRepository(db)

    def get_for_date(self, service_date: date) -> Optional[Dict[str, Any]]:
        row = self.generations.latest_for_date(service_date)
        if row is None:
            return None
        return generation_to_response(row, cached=True)

    def get_latest(self) -> Optional[Dict[str, Any]]:
        row = self.generations.latest()
        if row is None:
            return None
        return generation_to_response(row, cached=True)

    def generate(
        self,
        *,
        regenerate: bool = False,
        provider: Optional[str] = None,
        cost_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        service_date = service_date_now(self.settings)

        if not regenerate:
            existing = self.generations.latest_for_date(service_date)
            if existing is not None:
                return generation_to_response(existing, cached=True)

        active_waypoints = list(self.waypoints.list(active_only=True))
        active_vehicles = list(self.vehicles.list(active_only=True))
        request_payload = build_engine_payload(
            active_waypoints,
            active_vehicles,
            provider=provider,
            cost_mode=cost_mode,
        )

        engine_response = self.engine_client.generate_routes(request_payload)

        row = RouteGenerationRow(
            service_date=service_date,
            generated_at=now_naive_local(self.settings),
            provider=str(engine_response.get("provider", provider or "")),
            cost_mode=str(engine_response.get("cost_mode", cost_mode or "")),
            was_regenerated=regenerate,
            engine_request_json=request_payload,
            engine_response_json=engine_response,
        )
        saved = self.generations.create(row)
        return generation_to_response(saved, cached=False)
