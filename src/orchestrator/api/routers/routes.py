from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from orchestrator.api.schemas import GenerateRoutesBody, RouteGenerationOut
from orchestrator.db import get_db
from orchestrator.services.engine_client import EngineClientError
from orchestrator.services.route_service import (
    RouteService,
    RouteServiceError,
    service_date_now,
)

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
def get_route_today(db: Session = Depends(get_db)):
    service = RouteService(db)
    result = service.get_for_date(service_date_now())
    if result is None:
        raise HTTPException(status_code=404, detail="No route generated for today.")
    return result


@router.get("/{service_date}", response_model=RouteGenerationOut)
def get_route_for_date(service_date: date, db: Session = Depends(get_db)):
    service = RouteService(db)
    result = service.get_for_date(service_date)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No route generated for {service_date.isoformat()}.",
        )
    return result
