from fastapi import APIRouter

from orchestrator.constants import API_HEALTH_PATH
from orchestrator.services.health_checks import collect_health

router = APIRouter(tags=["health"])


@router.get(API_HEALTH_PATH)
def health():
    """Report orchestrator, database, route-engine, and OSRM reachability."""
    return collect_health()
