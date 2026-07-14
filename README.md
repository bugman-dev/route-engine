# Route Engine

A generic multi-vehicle route generation engine exposed as an HTTP API.
Given a depot, demand waypoints, and a vehicle fleet with capacities, it
builds feasible routes that minimize total travel cost using Google OR-Tools
(CVRP).

The same engine can power office cab allocation, delivery fleets, field
service, or any similar capacitated routing problem. All input and output
goes through JSON request/response payloads.

## Current capabilities

- HTTP API (FastAPI) — sole input/output surface
- Capacitated vehicle routing (assign stops to vehicles and order them)
- Capacity validation (total demand vs fleet capacity)
- Distance providers:
  - **Haversine** — straight-line km only (works offline)
  - **OSRM** — road-network distance km + duration (ETA) seconds
- Cost selection (`distance` or `eta`); with OSRM, each route includes both
  distance and duration details regardless of which one was optimized

## Not yet implemented

- Auth / rate limiting
- External / persistent input sources
- Self-hosted / private OSRM for production (the public
  `router.project-osrm.org` demo is fine for development only)

## Stack (today)

- Python 3.9+
- FastAPI + Uvicorn
- Google OR-Tools
- Pydantic
- OSRM (optional; HTTP Table service)

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e .
```

Copy the sample env file and edit if needed:

```bash
# Windows
copy .env.sample .env

# macOS / Linux
cp .env.sample .env
```

| Variable | Values | Meaning |
|----------|--------|---------|
| `ROUTE_ENGINE_PROVIDER` | `haversine` \| `osrm` | Default travel matrix source |
| `ROUTE_ENGINE_COST` | `distance` \| `eta` | Default matrix OR-Tools minimizes |
| `OSRM_BASE_URL` | URL | OSRM server (when provider is `osrm`) |

Request body may override `provider` and `cost_mode`. With **haversine**, only
distance exists — `cost_mode=eta` is ignored.

`.env` is gitignored; `.env.sample` is the committed template.

## Run the API

```bash
uvicorn route_engine.api.app:app --reload
```

Or:

```bash
route-engine-api
```

- Docs: http://127.0.0.1:8000/docs
- Health: `GET /health`
- Generate: `POST /api/v1/routes/generate`

### Example request

```bash
curl -X POST http://127.0.0.1:8000/api/v1/routes/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"waypoints\":[{\"id\":\"DEPOT\",\"name\":\"Depot\",\"latitude\":8.5241,\"longitude\":76.9366,\"demand\":0},{\"id\":\"WP001\",\"name\":\"Waypoint 1\",\"latitude\":8.5588,\"longitude\":76.8812},{\"id\":\"WP002\",\"name\":\"Waypoint 2\",\"latitude\":8.5104,\"longitude\":76.8987},{\"id\":\"WP003\",\"name\":\"Waypoint 3\",\"latitude\":8.6050,\"longitude\":76.9500}],\"vehicles\":[{\"id\":\"VH001\",\"number\":\"KL01TS1001\",\"operator\":\"James\",\"capacity\":4},{\"id\":\"VH002\",\"number\":\"KL01TS2002\",\"operator\":\"Thomas\",\"capacity\":3}],\"depot\":0,\"provider\":\"haversine\",\"cost_mode\":\"distance\"}"
```

macOS / Linux:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/routes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "waypoints": [
      {"id": "DEPOT", "name": "Depot", "latitude": 8.5241, "longitude": 76.9366, "demand": 0},
      {"id": "WP001", "name": "Waypoint 1", "latitude": 8.5588, "longitude": 76.8812},
      {"id": "WP002", "name": "Waypoint 2", "latitude": 8.5104, "longitude": 76.8987},
      {"id": "WP003", "name": "Waypoint 3", "latitude": 8.6050, "longitude": 76.9500}
    ],
    "vehicles": [
      {"id": "VH001", "number": "KL01TS1001", "operator": "James", "capacity": 4},
      {"id": "VH002", "number": "KL01TS2002", "operator": "Thomas", "capacity": 3}
    ],
    "depot": 0,
    "provider": "haversine",
    "cost_mode": "distance"
  }'
```

### Example response shape (OSRM)

```json
{
  "provider": "osrm",
  "cost_mode": "eta",
  "routes": [
    {
      "vehicle_id": "VH001",
      "vehicle_number": "KL01TS1001",
      "operator": "James",
      "capacity": 4,
      "stops": ["Depot", "Waypoint 12", "Waypoint 2", "Depot"],
      "cost_mode": "eta",
      "etas_seconds": [0, 462, 1132, 1699],
      "total_duration_seconds": 1699,
      "leg_distances_km": [5, 2, 8],
      "total_distance_km": 15
    }
  ]
}
```

With OSRM, routes always include both duration (`etas_seconds`,
`total_duration_seconds`) and distance (`leg_distances_km`,
`total_distance_km`). `cost_mode` only chooses what OR-Tools minimizes.
With Haversine, only distance fields are populated (no road ETAs).

## Core library (in-process)

```python
from route_engine import generate_routes
from route_engine.services.distance import HaversineDistanceProvider

routes = generate_routes(
    waypoints,
    vehicles,
    depot,
    distance_provider=HaversineDistanceProvider(),
    cost_mode="distance",
)
```

## Project layout

```text
src/route_engine/
  api/              # FastAPI — sole HTTP entrypoint
  constants.py      # shared strings (cost modes, providers, env keys)
  engine/           # orchestration + OR-Tools solver
  models/           # Waypoint, Vehicle, Route
  services/
    distance/       # Haversine + OSRM providers
    provider_factory.py
  validators/
  utils/
```

## Roadmap

1. Document and support a local/private OSRM setup for production use
2. Richer constraints (time windows, skills, etc.) as needed
