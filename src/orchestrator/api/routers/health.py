from fastapi import APIRouter

from orchestrator.constants import API_HEALTH_PATH
from orchestrator.db import ping_db

router = APIRouter(tags=["health"])


@router.get(API_HEALTH_PATH)
def health():
    db_ok = ping_db()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "unavailable",
    }
