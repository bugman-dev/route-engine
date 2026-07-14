"""OSRM road-network distance and duration matrices."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import List, Optional

from ...constants import (
    DEFAULT_OSRM_BASE_URL,
    DEFAULT_OSRM_PROFILE,
    DEFAULT_OSRM_TIMEOUT_SECONDS,
    OSRM_ANNOTATION_DISTANCE,
    OSRM_ANNOTATION_DURATION,
    OSRM_ANNOTATIONS,
    OSRM_METRES_TO_KM,
)
from ...models.waypoint import Waypoint
from .matrices import TravelMatrices


class OsrmDistanceProvider:
    """
    Road-network travel costs via OSRM's Table service.

    Requests both distance (metres → km) and duration (seconds) in one call.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_OSRM_BASE_URL,
        profile: str = DEFAULT_OSRM_PROFILE,
        timeout_seconds: float = DEFAULT_OSRM_TIMEOUT_SECONDS,
    ):
        self.base_url = base_url.rstrip("/")
        self.profile = profile
        self.timeout_seconds = timeout_seconds

    def matrix(self, waypoints: List[Waypoint]) -> TravelMatrices:
        if not waypoints:
            return TravelMatrices(distance_km=[], duration_seconds=[])

        # OSRM expects longitude,latitude (not lat,lon).
        coordinates = ";".join(
            f"{wp.longitude},{wp.latitude}" for wp in waypoints
        )
        url = (
            f"{self.base_url}/table/v1/{self.profile}/{coordinates}"
            f"?annotations={OSRM_ANNOTATIONS}"
        )

        try:
            with urllib.request.urlopen(url, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"OSRM table request failed ({exc.code}): {body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Could not reach OSRM at {self.base_url}: {exc.reason}"
            ) from exc

        if payload.get("code") != "Ok":
            raise RuntimeError(f"OSRM returned an error: {payload}")

        distances_m = payload.get("distances")
        durations_s = payload.get("durations")
        if distances_m is None or durations_s is None:
            raise RuntimeError(
                "OSRM response missing 'distances' or 'durations'. "
                f"Request with annotations={OSRM_ANNOTATIONS}."
            )

        return TravelMatrices(
            distance_km=self._to_int_matrix(
                distances_m,
                scale=OSRM_METRES_TO_KM,
                label=OSRM_ANNOTATION_DISTANCE,
            ),
            duration_seconds=self._to_int_matrix(
                durations_s,
                scale=1.0,
                label=OSRM_ANNOTATION_DURATION,
            ),
        )

    @staticmethod
    def _to_int_matrix(
        values: List[List[Optional[float]]],
        scale: float,
        label: str,
    ) -> List[List[int]]:
        matrix: List[List[int]] = []
        for i, row in enumerate(values):
            converted: List[int] = []
            for j, cell in enumerate(row):
                if cell is None:
                    raise RuntimeError(
                        f"OSRM found no road {label} between waypoints "
                        f"[{i}] and [{j}]."
                    )
                converted.append(round(cell * scale))
            matrix.append(converted)
        return matrix
