"""Run the Route Engine HTTP API with uvicorn."""

import uvicorn


def main() -> None:
    uvicorn.run(
        "route_engine.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
