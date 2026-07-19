"""Shared strings and constants reused across the route engine."""

from typing import Literal

# ---------------------------------------------------------------------------
# Cost modes (OR-Tools objective matrix)
# ---------------------------------------------------------------------------
COST_MODE_DISTANCE = "distance"
COST_MODE_ETA = "eta"
COST_MODES = (COST_MODE_DISTANCE, COST_MODE_ETA)
CostMode = Literal["distance", "eta"]
DEFAULT_COST_MODE = COST_MODE_DISTANCE

# ---------------------------------------------------------------------------
# Travel providers
# ---------------------------------------------------------------------------
PROVIDER_HAVERSINE = "haversine"
PROVIDER_OSRM = "osrm"
PROVIDERS = (PROVIDER_HAVERSINE, PROVIDER_OSRM)
DEFAULT_PROVIDER = PROVIDER_HAVERSINE
ProviderName = Literal["haversine", "osrm"]

# ---------------------------------------------------------------------------
# Environment variable names
# ---------------------------------------------------------------------------
ENV_PROVIDER = "ROUTE_ENGINE_PROVIDER"
ENV_COST = "ROUTE_ENGINE_COST"
ENV_OSRM_BASE_URL = "OSRM_BASE_URL"

# ---------------------------------------------------------------------------
# OSRM defaults
# ---------------------------------------------------------------------------
DEFAULT_OSRM_BASE_URL = "https://router.project-osrm.org"
DEFAULT_OSRM_PROFILE = "driving"
DEFAULT_OSRM_TIMEOUT_SECONDS = 30.0
OSRM_ANNOTATION_DISTANCE = "distance"
OSRM_ANNOTATION_DURATION = "duration"
OSRM_ANNOTATIONS = f"{OSRM_ANNOTATION_DISTANCE},{OSRM_ANNOTATION_DURATION}"
# Convert OSRM metres → kilometres for the distance matrix.
OSRM_METRES_TO_KM = 0.001

# ---------------------------------------------------------------------------
# HTTP API
# ---------------------------------------------------------------------------
API_PREFIX = "/api/v1"
API_ROUTES_GENERATE_PATH = "/routes/generate"
API_HEALTH_PATH = "/health"
