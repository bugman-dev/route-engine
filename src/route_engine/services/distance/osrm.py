"""OSRM road-network distance matrix provider."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import List

from ...models.waypoint import Waypoint

# Public demo server — fine for learning; use your own OSRM in production.
DEFAULT_OSRM_BASE_URL = "https://router.project-osrm.org"


class OsrmDistanceProvider:
    """
    Road-network distances via OSRM's Table service.

    Calls GET /table/v1/{profile}/{lon},{lat};...?annotations=distance
    and returns a km matrix (metres ÷ 1000, rounded) so units match Haversine.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_OSRM_BASE_URL,
        profile: str = "driving",
        timeout_seconds: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.profile = profile
        self.timeout_seconds = timeout_seconds

    def matrix(self, waypoints: List[Waypoint]) -> List[List[int]]:
        if not waypoints:
            return []

        # OSRM expects longitude,latitude (not lat,lon).
        coordinates = ";".join(
            f"{wp.longitude},{wp.latitude}" for wp in waypoints
        )
        url = (
            f"{self.base_url}/table/v1/{self.profile}/{coordinates}"
            f"?annotations=distance"
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
        if distances_m is None:
            raise RuntimeError(
                "OSRM response missing 'distances'. "
                "Request with annotations=distance."
            )

        return self._to_km_matrix(distances_m)

    @staticmethod
    def _to_km_matrix(distances_m: List[List[float | None]]) -> List[List[int]]:
        matrix: List[List[int]] = []
        for i, row in enumerate(distances_m):
            converted: List[int] = []
            for j, metres in enumerate(row):
                if metres is None:
                    raise RuntimeError(
                        f"OSRM found no road route between waypoints "
                        f"[{i}] and [{j}]."
                    )
                converted.append(round(metres / 1000))
            matrix.append(converted)
        return matrix
