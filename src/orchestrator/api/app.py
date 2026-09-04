"""FastAPI application — public orchestrator entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from orchestrator.api.routers import health, routes, vehicles, waypoints
from orchestrator.config import load_env
from orchestrator.constants import API_PREFIX
from orchestrator.db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_env()
    init_db()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="Route Orchestrator",
        description=(
            "Public API for waypoints, vehicles, and daily route generation. "
            "Persists data in MySQL and calls the internal route-engine over HTTP."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    application.include_router(health.router)
    application.include_router(waypoints.router, prefix=API_PREFIX)
    application.include_router(vehicles.router, prefix=API_PREFIX)
    application.include_router(routes.router, prefix=API_PREFIX)
    return application


app = create_app()
