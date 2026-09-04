from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from orchestrator.api.schemas import GenerateRoutesBody, RouteGenerationOut
from orchestrator.db import get_db
from orchestrator.services.engine_client import EngineClientError
from orchestrator.services.route_service import RouteService, RouteServiceError

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/generate", response_model=RouteGenerationOut)
def generate_routes(body: GenerateRoutesBody, db: Session = Depends(get_db)):
    service = RouteService(db)
    try:
        return service.generate(
            regenerate=body.regenerate,
            provider=body.provider,
            cost_mode=body.cost_mode,
        )
    except RouteServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except EngineClientError as exc:
        status = 502
        if exc.status_code and 400 <= exc.status_code < 500:
            status = 400
        raise HTTPException(status_code=status, detail=str(exc)) from exc


@router.get("", response_model=RouteGenerationOut)
def get_routes(
    service_date: Optional[date] = Query(
        None,
        description=(
            "If set, return the latest generation for that date. "
            "If omitted, return the most recently generated route set."
        ),
    ),
    db: Session = Depends(get_db),
):
    """Fetch routes: latest overall, or filtered by optional service_date."""
    service = RouteService(db)
    if service_date is not None:
        result = service.get_for_date(service_date)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"No route generated for {service_date.isoformat()}.",
            )
        return result

    result = service.get_latest()
    if result is None:
        raise HTTPException(
            status_code=404, detail="No routes have been generated yet."
        )
    return result
