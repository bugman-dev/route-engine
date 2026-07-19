"""HTTP API tests via FastAPI TestClient."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from route_engine.api.app import app
from route_engine.constants import COST_MODE_DISTANCE, PROVIDER_HAVERSINE


@pytest.fixture
def client():
    return TestClient(app)


def _valid_body(**overrides):
    body = {
        "waypoints": [
            {
                "id": "DEPOT",
                "name": "Depot",
                "latitude": 8.5241,
                "longitude": 76.9366,
                "demand": 0,
            },
            {
                "id": "WP1",
                "name": "Stop A",
                "latitude": 8.5400,
                "longitude": 76.9100,
            },
            {
                "id": "WP2",
                "name": "Stop B",
                "latitude": 8.5104,
                "longitude": 76.8987,
            },
        ],
        "vehicles": [
            {
                "id": "VH1",
                "number": "KA01",
                "operator": "Alex",
                "capacity": 4,
            }
        ],
        "depot": 0,
        "provider": "haversine",
        "cost_mode": "distance",
    }
    body.update(overrides)
    return body


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_happy_path_haversine(client):
    response = client.post("/api/v1/routes/generate", json=_valid_body())
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == PROVIDER_HAVERSINE
    assert payload["cost_mode"] == COST_MODE_DISTANCE
    assert payload["routes"]
    assert payload["routes"][0]["stops"][0] == "Depot"
    assert payload["routes"][0]["stops"][-1] == "Depot"


def test_generate_returns_400_when_capacity_insufficient(client):
    body = _valid_body(
        vehicles=[
            {
                "id": "VH1",
                "number": "KA01",
                "operator": "Alex",
                "capacity": 1,  # 2 demand stops → fails
            }
        ]
    )
    response = client.post("/api/v1/routes/generate", json=body)
    assert response.status_code == 400
    assert "capacity" in response.json()["detail"].lower()


def test_generate_returns_400_for_invalid_cost_mode(client):
    response = client.post(
        "/api/v1/routes/generate",
        json=_valid_body(cost_mode="warp-speed"),
    )
    # Pydantic rejects invalid Literal before the handler → 422
    assert response.status_code == 422


def test_generate_returns_502_when_osrm_provider_fails(client):
    class BrokenOsrm:
        def matrix(self, waypoints):
            raise RuntimeError("Could not reach OSRM at http://osrm:5000")

    with patch(
        "route_engine.api.deps.build_distance_provider",
        return_value=BrokenOsrm(),
    ):
        response = client.post(
            "/api/v1/routes/generate",
            json=_valid_body(provider="osrm"),
        )

    assert response.status_code == 502
    assert "OSRM" in response.json()["detail"]
