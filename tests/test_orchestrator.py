"""Orchestrator service tests (SQLite + mocked engine client)."""

from __future__ import annotations

import os
from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

# Configure test DB before importing app modules that cache settings.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ENGINE_BASE_URL"] = "http://engine.test"
os.environ["ORCHESTRATOR_TZ"] = "Asia/Kolkata"

from orchestrator.db import init_db, reset_engine_for_tests  # noqa: E402
from orchestrator.db.models import VehicleRow, WaypointRow  # noqa: E402
from orchestrator.db.repositories import (  # noqa: E402
    RouteGenerationRepository,
    VehicleRepository,
    WaypointRepository,
)
from orchestrator.services.route_service import (  # noqa: E402
    RouteService,
    RouteServiceError,
    build_engine_payload,
)


@pytest.fixture(autouse=True)
def _fresh_db(tmp_path, monkeypatch):
    db_path = tmp_path / "orch.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("ENGINE_BASE_URL", "http://engine.test")
    monkeypatch.setenv("ORCHESTRATOR_TZ", "Asia/Kolkata")
    reset_engine_for_tests()
    init_db()
    yield
    reset_engine_for_tests()


@pytest.fixture
def db_session():
    from orchestrator.db import get_session_factory

    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _seed_fleet(db_session):
    wp_repo = WaypointRepository(db_session)
    vh_repo = VehicleRepository(db_session)
    depot = wp_repo.create(
        WaypointRow(
            external_id="DEPOT",
            name="Depot",
            latitude=8.52,
            longitude=76.93,
            demand=0,
            is_depot=True,
            is_active=True,
        )
    )
    stop = wp_repo.create(
        WaypointRow(
            external_id="WP1",
            name="Stop A",
            latitude=8.54,
            longitude=76.91,
            demand=1,
            is_depot=False,
            is_active=True,
        )
    )
    inactive = wp_repo.create(
        WaypointRow(
            external_id="WP_OFF",
            name="Inactive",
            latitude=8.55,
            longitude=76.92,
            demand=1,
            is_depot=False,
            is_active=False,
        )
    )
    vehicle = vh_repo.create(
        VehicleRow(
            external_id="VH1",
            number="KA01",
            operator="Alex",
            capacity=4,
            is_active=True,
        )
    )
    return depot, stop, inactive, vehicle


def test_build_engine_payload_puts_depot_first(db_session):
    depot, stop, _inactive, vehicle = _seed_fleet(db_session)
    waypoints = list(WaypointRepository(db_session).list(active_only=True))
    vehicles = list(VehicleRepository(db_session).list(active_only=True))

    payload = build_engine_payload(waypoints, vehicles, provider="haversine")
    assert payload["depot"] == 0
    assert payload["waypoints"][0]["id"] == "DEPOT"
    assert payload["waypoints"][0]["name"] == "Depot"
    assert len(payload["waypoints"]) == 2
    assert payload["vehicles"][0]["id"] == "VH1"
    assert payload["provider"] == "haversine"


def test_build_engine_payload_requires_single_depot(db_session):
    WaypointRepository(db_session).create(
        WaypointRow(
            name="Only stop",
            latitude=1.0,
            longitude=2.0,
            demand=1,
            is_depot=False,
            is_active=True,
        )
    )
    vehicles = [
        VehicleRepository(db_session).create(
            VehicleRow(number="N1", operator="O", capacity=2, is_active=True)
        )
    ]
    waypoints = list(WaypointRepository(db_session).list(active_only=True))
    with pytest.raises(RouteServiceError, match="depot"):
        build_engine_payload(waypoints, vehicles)


def test_generate_caches_same_day_unless_regenerate(db_session):
    _seed_fleet(db_session)
    client = MagicMock()
    client.generate_routes.return_value = {
        "provider": "haversine",
        "cost_mode": "distance",
        "routes": [
            {
                "vehicle_id": "VH1",
                "vehicle_number": "KA01",
                "operator": "Alex",
                "capacity": 4,
                "stops": ["Depot", "Stop A", "Depot"],
                "cost_mode": "distance",
            }
        ],
    }

    service = RouteService(db_session, engine_client=client)
    first = service.generate(regenerate=False)
    assert first["cached"] is False
    assert client.generate_routes.call_count == 1

    second = service.generate(regenerate=False)
    assert second["cached"] is True
    assert client.generate_routes.call_count == 1
    assert second["routes"] == first["routes"]

    third = service.generate(regenerate=True)
    assert third["cached"] is False
    assert third["was_regenerated"] is True
    assert client.generate_routes.call_count == 2
    assert RouteGenerationRepository(db_session).latest_for_date(
        date.fromisoformat(third["service_date"])
    )


def test_api_waypoints_and_generate_with_mock_engine(db_session, monkeypatch):
    # Rebuild FastAPI app dependencies against the test DB.
    from orchestrator.api.app import create_app
    from orchestrator.services import route_service as route_service_module

    fake_client = MagicMock()
    fake_client.generate_routes.return_value = {
        "provider": "haversine",
        "cost_mode": "distance",
        "routes": [{"vehicle_id": "1", "stops": ["Depot", "A", "Depot"]}],
    }

    class FakeRouteService(route_service_module.RouteService):
        def __init__(self, db, engine_client=None, settings=None):
            super().__init__(db, engine_client=fake_client, settings=settings)

    monkeypatch.setattr(route_service_module, "RouteService", FakeRouteService)
    monkeypatch.setattr(
        "orchestrator.api.routers.routes.RouteService", FakeRouteService
    )

    app = create_app()
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["database"] == "ok"

    created_waypoints = client.post(
        "/api/v1/waypoints",
        json=[
            {
                "external_id": "DEPOT",
                "name": "Depot",
                "latitude": 8.52,
                "longitude": 76.93,
                "demand": 0,
                "is_depot": True,
            },
            {
                "name": "Stop A",
                "latitude": 8.54,
                "longitude": 76.91,
            },
        ],
    )
    assert created_waypoints.status_code == 201
    assert len(created_waypoints.json()) == 2

    created_vehicles = client.post(
        "/api/v1/vehicles",
        json=[{"number": "KA01", "operator": "Alex", "capacity": 4}],
    )
    assert created_vehicles.status_code == 201
    assert len(created_vehicles.json()) == 1

    listed = client.get("/api/v1/waypoints", params={"active_only": True})
    assert listed.status_code == 200
    assert len(listed.json()) == 2

    total_waypoints = client.get("/api/v1/waypoints/total")
    assert total_waypoints.status_code == 200
    assert total_waypoints.json() == {"total_waypoints": 2, "active_only": True}

    total_demand = client.get("/api/v1/waypoints/demand/total")
    assert total_demand.status_code == 200
    assert total_demand.json() == {"total_demand": 1, "active_only": True}

    total_vehicles = client.get("/api/v1/vehicles/total")
    assert total_vehicles.status_code == 200
    assert total_vehicles.json() == {"total_vehicles": 1, "active_only": True}

    total_capacity = client.get("/api/v1/vehicles/capacity/total")
    assert total_capacity.status_code == 200
    assert total_capacity.json() == {"total_capacity": 4, "active_only": True}

    generated = client.post("/api/v1/routes/generate", json={"regenerate": False})
    assert generated.status_code == 200
    body = generated.json()
    assert body["cached"] is False
    assert body["routes"]

    cached = client.post("/api/v1/routes/generate", json={})
    assert cached.status_code == 200
    assert cached.json()["cached"] is True

    latest = client.get("/api/v1/routes")
    assert latest.status_code == 200
    assert latest.json()["routes"]
    assert latest.json()["service_date"] == generated.json()["service_date"]

    by_date = client.get(f"/api/v1/routes/{generated.json()['service_date']}")
    assert by_date.status_code == 200
    assert by_date.json()["routes"]
