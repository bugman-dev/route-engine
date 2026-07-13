# Route Engine

A generic multi-vehicle route generation engine. Given a depot, demand
waypoints, and a vehicle fleet with capacities, it builds feasible routes
that minimize total travel distance using Google OR-Tools (CVRP).

The same engine can power office cab allocation, delivery fleets, field
service, or any similar capacitated routing problem. Domain-specific data
stays outside the core — see `examples/` for a sample dataset.

## Current capabilities

- Capacitated vehicle routing (assign stops to vehicles and order them)
- Capacity validation (total demand vs fleet capacity)
- Distance providers:
  - **Haversine** — straight-line km (default, works offline)
  - **OSRM** — road-network km via the Table API
- CLI demo with sample data

## Not yet implemented

- HTTP API (FastAPI)
- ETA enrichment on routes (OSRM also returns durations — next step)
- External / persistent input sources

## Stack (today)

- Python 3.9+
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
| `ROUTE_ENGINE_PROVIDER` | `haversine` \| `osrm` | Distance matrix source |
| `OSRM_BASE_URL` | URL | OSRM server (when provider is `osrm`) |

`.env` is gitignored; `.env.sample` is the committed template.

## Run

Uses settings from `.env`. Override on the CLI if you want:

```bash
python -m route_engine
python -m route_engine --provider osrm
```

Example `.env` for a local OSRM instance:

```env
ROUTE_ENGINE_PROVIDER=osrm
OSRM_BASE_URL=http://localhost:5000
```

You should see printed routes shaped like:

```text
Vehicle: KL01TS1001
Operator: James
Depot -> Waypoint 4 -> Waypoint 5 -> ... -> Depot
```

## Core API

```python
from route_engine import generate_routes
from route_engine.examples.sample_data import get_waypoints, get_vehicles, get_depot
from route_engine.services.distance import OsrmDistanceProvider

routes = generate_routes(
    get_waypoints(),
    get_vehicles(),
    get_depot(),
    distance_provider=OsrmDistanceProvider(),
)
```

| Input | Meaning |
|--------|---------|
| `waypoints` | Locations to visit; index `depot` is start/end |
| `vehicles` | Fleet with per-vehicle `capacity` |
| `depot` | Index of the depot in `waypoints` |
| `distance_provider` | Optional; defaults to Haversine |

Output: a list of `Route` objects (vehicle metadata + ordered stop names).

## Project layout

```text
src/route_engine/
  engine/           # orchestration + OR-Tools solver
  models/           # Waypoint, Vehicle, Route
  services/
    distance/       # Haversine + OSRM providers
  validators/
  utils/
  examples/         # sample datasets (not part of the core API)
  cli.py            # demo entrypoint
```

## Roadmap

1. ETA / duration on route responses (reuse OSRM durations)
2. FastAPI service wrapping `generate_routes`
3. Richer constraints (time windows, skills, etc.) as needed
