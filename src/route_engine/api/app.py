"""FastAPI application — sole HTTP entrypoint for the route engine."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from route_engine.api.routers import health, routes
from route_engine.config import load_env
from route_engine.constants import API_PREFIX


@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_env()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="Route Engine",
        description=(
            "Capacitated multi-vehicle route generation. "
            "Send waypoints and vehicles; receive optimized routes."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    application.include_router(health.router)
    application.include_router(routes.router, prefix=API_PREFIX)
    return application


app = create_app()
