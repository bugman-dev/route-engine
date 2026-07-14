from fastapi import APIRouter, HTTPException

from route_engine.api.deps import resolve_cost_mode, resolve_distance_provider
from route_engine.api.schemas import GenerateRoutesRequest, GenerateRoutesResponse
from route_engine.constants import (
    API_ROUTES_GENERATE_PATH,
    COST_MODE_DISTANCE,
    PROVIDER_HAVERSINE,
)
from route_engine.engine.route_engine import generate_routes

router = APIRouter(tags=["routes"])


@router.post(API_ROUTES_GENERATE_PATH, response_model=GenerateRoutesResponse)
def generate_routes_endpoint(body: GenerateRoutesRequest) -> GenerateRoutesResponse:
    try:
        provider_name, distance_provider = resolve_distance_provider(body.provider)
        cost_mode = resolve_cost_mode(body.cost_mode)
        routes = generate_routes(
            body.waypoints,
            body.vehicles,
            body.depot,
            distance_provider=distance_provider,
            cost_mode=cost_mode,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if routes:
        resolved_cost = routes[0].cost_mode
    elif provider_name == PROVIDER_HAVERSINE:
        resolved_cost = COST_MODE_DISTANCE
    else:
        resolved_cost = cost_mode

    return GenerateRoutesResponse(
        provider=provider_name,
        cost_mode=resolved_cost,
        routes=routes,
    )
