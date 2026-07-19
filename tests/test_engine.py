"""Engine-level tests (no HTTP)."""

import pytest

from route_engine.constants import COST_MODE_DISTANCE, COST_MODE_ETA
from route_engine.engine.route_engine import generate_routes
from route_engine.services.distance import HaversineDistanceProvider
from route_engine.validators.capacity_validator import validate_capacity

from tests.conftest import FakeTravelProvider, square_matrix


def test_capacity_rejects_when_seats_insufficient(depot_and_stops, vehicles_too_small):
    with pytest.raises(ValueError, match="Not enough capacity"):
        validate_capacity(depot_and_stops, vehicles_too_small)


def test_generate_routes_raises_on_insufficient_capacity(
    depot_and_stops, vehicles_too_small
):
    with pytest.raises(ValueError, match="Not enough capacity"):
        generate_routes(
            depot_and_stops,
            vehicles_too_small,
            depot=0,
            distance_provider=HaversineDistanceProvider(),
        )


def test_haversine_forces_distance_even_when_cost_mode_is_eta(
    depot_and_stops, vehicles_enough
):
    routes = generate_routes(
        depot_and_stops,
        vehicles_enough,
        depot=0,
        distance_provider=HaversineDistanceProvider(),
        cost_mode=COST_MODE_ETA,
    )

    assert routes
    assert all(route.cost_mode == COST_MODE_DISTANCE for route in routes)
    # Haversine has no duration matrix.
    assert all(route.etas_seconds is None for route in routes)
    assert all(route.total_duration_seconds is None for route in routes)
    # Distance along the chosen path is still annotated.
    assert all(route.leg_distances_km is not None for route in routes)
    assert all(route.total_distance_km is not None for route in routes)


def test_osrm_like_distance_cost_returns_both_metrics(
    depot_and_stops, vehicles_enough, osrm_like_provider
):
    routes = generate_routes(
        depot_and_stops,
        vehicles_enough,
        depot=0,
        distance_provider=osrm_like_provider,
        cost_mode=COST_MODE_DISTANCE,
    )

    assert routes
    assert all(route.cost_mode == COST_MODE_DISTANCE for route in routes)
    for route in routes:
        assert route.etas_seconds is not None
        assert route.total_duration_seconds is not None
        assert route.leg_distances_km is not None
        assert route.total_distance_km is not None
        assert len(route.etas_seconds) == len(route.stops)
        assert route.etas_seconds[0] == 0
        assert route.total_duration_seconds == route.etas_seconds[-1]
        assert route.total_distance_km == sum(route.leg_distances_km)


def test_osrm_like_eta_cost_returns_both_metrics(
    depot_and_stops, vehicles_enough, osrm_like_provider
):
    routes = generate_routes(
        depot_and_stops,
        vehicles_enough,
        depot=0,
        distance_provider=osrm_like_provider,
        cost_mode=COST_MODE_ETA,
    )

    assert routes
    assert all(route.cost_mode == COST_MODE_ETA for route in routes)
    for route in routes:
        assert route.etas_seconds is not None
        assert route.total_duration_seconds is not None
        assert route.leg_distances_km is not None
        assert route.total_distance_km is not None


def test_invalid_cost_mode_raises(depot_and_stops, vehicles_enough):
    with pytest.raises(ValueError, match="Invalid cost_mode"):
        generate_routes(
            depot_and_stops,
            vehicles_enough,
            depot=0,
            distance_provider=FakeTravelProvider(square_matrix(4, 5)),
            cost_mode="not-a-mode",  # type: ignore[arg-type]
        )
