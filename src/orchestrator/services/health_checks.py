"""Dependency health probes for the orchestrator."""

from __future__ import annotations

import urllib.error
import urllib.request
from typing import Dict, Optional

from orchestrator.config import Settings, get_settings
from orchestrator.db import ping_db

# osrm-routed's /health returns 400 on some builds; nearest is a reliable probe.
OSRM_HEALTH_PATH = "/nearest/v1/driving/0,0"


def _status_label(ok: bool) -> str:
    return "ok" if ok else "unavailable"


def check_http_reachable(url: str, timeout_seconds: float) -> bool:
    """Return True if GET url responds with HTTP 2xx."""
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return 200 <= response.status < 300
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return False


def collect_health(settings: Optional[Settings] = None) -> Dict[str, str]:
    settings = settings or get_settings()
    timeout = settings.health_timeout_seconds

    database_ok = ping_db()
    engine_ok = check_http_reachable(
        f"{settings.engine_base_url}/health", timeout
    )
    osrm_ok = check_http_reachable(
        f"{settings.osrm_base_url}{OSRM_HEALTH_PATH}", timeout
    )

    all_ok = database_ok and engine_ok and osrm_ok
    return {
        "status": "ok" if all_ok else "degraded",
        "database": _status_label(database_ok),
        "engine": _status_label(engine_ok),
        "osrm": _status_label(osrm_ok),
    }
