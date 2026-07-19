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
- Docker Compose stack: route-engine + private OSRM on one network

## Not yet implemented

- Auth / rate limiting
- External / persistent input sources
- Automated / scheduled OSM map refresh for OSRM

## Stack (today)

- Python 3.9+
- FastAPI + Uvicorn
- Google OR-Tools
- Pydantic
- OSRM (optional; HTTP Table service; self-host via Docker)

## Setup (local, without Docker)

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
| `OSRM_MAP` | basename | Prepared map name under `osrm-data/` (Compose) |

Request body may override `provider` and `cost_mode`. With **haversine**, only
distance exists — `cost_mode=eta` is ignored.

`.env` is gitignored; `.env.sample` is the committed template.
Config reaches containers via Compose `env_file` (nothing secret is baked into the image).

## Run the API locally

```bash
python -m uvicorn route_engine.api.app:app --reload
```

Or:

```bash
route-engine-api
```

- Docs: http://127.0.0.1:8000/docs
- Health: `GET /health`
- Generate: `POST /api/v1/routes/generate`

## Run with Docker

Requires Docker Desktop (Linux containers).

```text
Client → route-engine (:8000) → osrm (:5000, private on compose network)
```

### 1. Env file

```bash
# Windows
copy .env.sample .env

# macOS / Linux
cp .env.sample .env
```

### 2. OSRM map data (download + prepare)

Map extracts and prepared graphs live under `osrm-data/`. They are **gitignored**
(only `osrm-data/README.md` is committed). Prefer a small region that covers your
service area — large extracts need much more RAM and time.

#### Download

1. Open [Geofabrik downloads](https://download.geofabrik.de/).
2. Pick a region (e.g. Asia → India → a state, or a custom zone extract).
3. Download the `.osm.pbf` file into `osrm-data/`.

Example (basename without extension is what you use everywhere else):

```text
osrm-data/southern-zone-260718.osm.pbf
→ OSRM_MAP=southern-zone-260718
```

#### Prepare the graph (one-time per map)

macOS / Linux:

```bash
chmod +x scripts/prepare_osrm.sh
./scripts/prepare_osrm.sh southern-zone-260718
```

Windows PowerShell (from the project root):

```powershell
$MAP = "southern-zone-260718"   # must match the .osm.pbf basename
$IMAGE = "ghcr.io/project-osrm/osrm-backend:v5.27.1"
$data = (Resolve-Path .\osrm-data).Path

docker run --rm -t -v "${data}:/data" $IMAGE `
  osrm-extract -p /opt/car.lua "/data/${MAP}.osm.pbf"

docker run --rm -t -v "${data}:/data" $IMAGE `
  osrm-partition "/data/${MAP}.osrm"

docker run --rm -t -v "${data}:/data" $IMAGE `
  osrm-customize "/data/${MAP}.osrm"
```

After this, `osrm-data/` will contain many `<map>.osrm.*` files. That is expected.

#### Point the app at the map

In `.env`:

```env
ROUTE_ENGINE_PROVIDER=osrm
OSRM_MAP=southern-zone-260718
```

(`OSRM_BASE_URL` is overridden to `http://osrm:5000` by Compose for the app.)

#### Replace / remove existing map data

Before installing a **new** region (or a newer extract of the same region),
stop the stack and clear the old files so they are not mixed:

```powershell
# From the project root
docker compose down

# Windows — remove everything except README.md
Get-ChildItem .\osrm-data -Exclude README.md | Remove-Item -Recurse -Force
```

```bash
# macOS / Linux
docker compose down
find osrm-data -mindepth 1 ! -name 'README.md' -exec rm -rf {} +
```

Then download the new `.osm.pbf`, run prepare again, update `OSRM_MAP` in `.env`,
and start Compose.

### 3. Start the stack

```bash
docker compose build
docker compose up
```

API docs: http://localhost:8000/docs

Notes:

- Keep OSRM private — only publish the FastAPI port (`8000`) in production.
- OSRM travel times are profile-based estimates (from `car.lua`), not live traffic.
- Until map data is prepared, you can leave `ROUTE_ENGINE_PROVIDER=haversine`
  and still start the app (OSRM will fail only when provider is `osrm`).
- If `docker pull ghcr.io/project-osrm/osrm-backend:...` fails with “denied”,
  try `docker logout ghcr.io` and pull again.

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
Dockerfile
docker-compose.yml
scripts/prepare_osrm.sh
osrm-data/          # map extracts + prepared graph (gitignored contents)
```

## Roadmap

1. Richer constraints (time windows, skills, etc.) as needed
2. Automated OSM refresh / map update pipeline for OSRM
