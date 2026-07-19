"""OsrmDistanceProvider unit tests with mocked HTTP (no live network)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from route_engine.models.waypoint import Waypoint
from route_engine.services.distance.osrm import OsrmDistanceProvider


def _waypoints():
    return [
        Waypoint(id="D", name="Depot", latitude=8.5, longitude=76.9, demand=0),
        Waypoint(id="A", name="A", latitude=8.51, longitude=76.91),
    ]


def _fake_urlopen(payload: dict, status: int = 200):
    body = json.dumps(payload).encode("utf-8")
    response = MagicMock()
    response.read.return_value = body
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    return response


def test_osrm_matrix_parses_distance_and_duration():
    payload = {
        "code": "Ok",
        "distances": [[0.0, 2600.0], [2600.0, 0.0]],  # metres → 3 km when rounded
        "durations": [[0.0, 180.0], [180.0, 0.0]],  # seconds
    }

    with patch(
        "route_engine.services.distance.osrm.urllib.request.urlopen",
        return_value=_fake_urlopen(payload),
    ) as mock_open:
        provider = OsrmDistanceProvider(base_url="http://osrm.test")
        matrices = provider.matrix(_waypoints())

    mock_open.assert_called_once()
    url = mock_open.call_args[0][0]
    assert url.startswith("http://osrm.test/table/v1/driving/")
    assert "annotations=distance,duration" in url

    assert matrices.distance_km == [[0, 3], [3, 0]]
    assert matrices.duration_seconds == [[0, 180], [180, 0]]


def test_osrm_unreachable_raises_runtime_error():
    import urllib.error

    with patch(
        "route_engine.services.distance.osrm.urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        provider = OsrmDistanceProvider(base_url="http://osrm.test")
        with pytest.raises(RuntimeError, match="Could not reach OSRM"):
            provider.matrix(_waypoints())


def test_osrm_bad_code_raises_runtime_error():
    payload = {"code": "NoRoute", "message": "boom"}

    with patch(
        "route_engine.services.distance.osrm.urllib.request.urlopen",
        return_value=_fake_urlopen(payload),
    ):
        provider = OsrmDistanceProvider(base_url="http://osrm.test")
        with pytest.raises(RuntimeError, match="OSRM returned an error"):
            provider.matrix(_waypoints())
