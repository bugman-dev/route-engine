"""Shared fixtures and fakes for route-engine tests."""

from __future__ import annotations

import pytest

from route_engine.models.vehicle import Vehicle
from route_engine.models.waypoint import Waypoint
from route_engine.services.distance.matrices import TravelMatrices


@pytest.fixture
def depot_and_stops():
    """One depot + three demand stops (Kerala-ish coords)."""
    return [
        Waypoint(
            id="DEPOT",
            name="Depot",
            latitude=8.5241,
            longitude=76.9366,
            demand=0,
        ),
        Waypoint(id="WP1", name="Stop A", latitude=8.5400, longitude=76.9100),
        Waypoint(id="WP2", name="Stop B", latitude=8.5104, longitude=76.8987),
        Waypoint(id="WP3", name="Stop C", latitude=8.5560, longitude=76.9300),
    ]


@pytest.fixture
def vehicles_enough():
    return [
        Vehicle(id="VH1", number="KA01", operator="Alex", capacity=2),
        Vehicle(id="VH2", number="KA02", operator="Blake", capacity=2),
    ]


@pytest.fixture
def vehicles_too_small():
    """Total capacity 2, but three demand stops → validation failure."""
    return [
        Vehicle(id="VH1", number="KA01", operator="Alex", capacity=2),
    ]


class FakeTravelProvider:
    """In-memory provider that returns fixed distance / optional duration matrices."""

    def __init__(self, distance_km, duration_seconds=None):
        self.distance_km = distance_km
        self.duration_seconds = duration_seconds

    def matrix(self, waypoints):
        n = len(waypoints)
        assert len(self.distance_km) == n
        if self.duration_seconds is not None:
            assert len(self.duration_seconds) == n
        return TravelMatrices(
            distance_km=self.distance_km,
            duration_seconds=self.duration_seconds,
        )


def square_matrix(size: int, fill: int, diagonal: int = 0):
    """Build an N×N matrix filled with `fill`, zeros on the diagonal by default."""
    return [
        [diagonal if i == j else fill for j in range(size)]
        for i in range(size)
    ]


@pytest.fixture
def osrm_like_provider():
    """4×4 matrices so tests can assert both distance and duration on routes."""
    # Asymmetric-ish costs so distance vs eta can prefer different arcs.
    distance_km = [
        [0, 10, 20, 15],
        [10, 0, 8, 12],
        [20, 8, 0, 9],
        [15, 12, 9, 0],
    ]
    duration_seconds = [
        [0, 600, 100, 900],
        [600, 0, 500, 700],
        [100, 500, 0, 400],
        [900, 700, 400, 0],
    ]
    return FakeTravelProvider(distance_km, duration_seconds)
