# Route Engine

A generic multi-vehicle route generation engine. Given a depot, demand
waypoints, and a vehicle fleet with capacities, it builds feasible routes
that minimize total travel cost using Google OR-Tools (CVRP).

The same engine can power office cab allocation, delivery fleets, field
service, or any similar capacitated routing problem. Domain-specific data
stays outside the core — see `examples/` for a sample dataset.

## Current capabilities

- Capacitated vehicle routing (assign stops to vehicles and order them)
- Capacity validation (total demand vs fleet capacity)
- Distance providers:
  - **Haversine** — straight-line km only (works offline)
  - **OSRM** — road-network distance km + duration (ETA) seconds
- Cost selection via `.env`: minimize **distance** or **eta**; the other
  metric is shown on each route (OSRM only)
- CLI demo with sample data

## Not yet implemented

- HTTP API (FastAPI)
- Wall-clock departure / arrival clocks
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
| `ROUTE_ENGINE_PROVIDER` | `haversine` \| `osrm` | Travel matrix source |
| `ROUTE_ENGINE_COST` | `distance` \| `eta` | Matrix OR-Tools minimizes |
| `OSRM_BASE_URL` | URL | OSRM server (when provider is `osrm`) |

With **haversine**, only distance exists — `ROUTE_ENGINE_COST` is ignored and
optimization always uses distance (no ETA in output).

With **osrm**, both matrices are built. The chosen cost is minimized; the
other metric is annotated on each route and printed.

`.env` is gitignored; `.env.sample` is the committed template.

## Run

Uses settings from `.env`. Override on the CLI if you want:

```bash
python -m route_engine
python -m route_engine --provider osrm --cost eta
```

Example `.env` for OSRM minimizing travel time:

```env
ROUTE_ENGINE_PROVIDER=osrm
ROUTE_ENGINE_COST=eta
OSRM_BASE_URL=https://router.project-osrm.org
```

You should see printed routes shaped like:

```text
Vehicle: KL01TS1001
Operator: James
Cost: distance
Depot -> Waypoint 4 -> ... -> Depot
ETA: Depot (+0s) -> Waypoint 4 (+12m) -> ... -> Depot (+25m)
Total duration: 25m
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
    cost_mode="distance",  # or "eta"
)
```

| Input | Meaning |
|--------|---------|
| `waypoints` | Locations to visit; index `depot` is start/end |
| `vehicles` | Fleet with per-vehicle `capacity` |
| `depot` | Index of the depot in `waypoints` |
| `distance_provider` | Optional; defaults to Haversine |
| `cost_mode` | `distance` or `eta` (forced to distance for Haversine) |

Output: a list of `Route` objects (vehicle metadata, stops, and the non-cost
metric when available).

## Project layout

```text
src/route_engine/
  engine/           # orchestration + OR-Tools solver
  models/           # Waypoint, Vehicle, Route
  services/
    distance/       # Haversine + OSRM providers (TravelMatrices)
  validators/
  utils/
  examples/         # sample datasets (not part of the core API)
  cli.py            # demo entrypoint
```

## Roadmap

1. FastAPI service wrapping `generate_routes`
2. Wall-clock ETAs from a configured departure time
3. Richer constraints (time windows, skills, etc.) as needed
