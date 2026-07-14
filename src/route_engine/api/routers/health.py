from fastapi import APIRouter

from route_engine.constants import API_HEALTH_PATH

router = APIRouter(tags=["health"])


@router.get(API_HEALTH_PATH)
def health():
    return {"status": "ok"}
