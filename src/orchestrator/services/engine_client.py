"""HTTP client for the internal route-engine service."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from orchestrator.config import Settings, get_settings


class EngineClientError(Exception):
    """Raised when the route-engine HTTP call fails."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class EngineClient:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    def generate_routes(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.settings.engine_base_url}/api/v1/routes/generate"
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.settings.engine_timeout_seconds
            ) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(detail)
                message = parsed.get("detail", detail)
            except json.JSONDecodeError:
                message = detail
            raise EngineClientError(
                f"Route engine error ({exc.code}): {message}",
                status_code=exc.code,
            ) from exc
        except urllib.error.URLError as exc:
            raise EngineClientError(
                f"Could not reach route engine at {self.settings.engine_base_url}: "
                f"{exc.reason}"
            ) from exc
