# Route Engine

A capacitated multi-vehicle route generation stack (CVRP) with:

- **Orchestrator** (public API, MySQL) — waypoints, vehicles, daily routes
- **Route engine** (internal) — OR-Tools optimization
- **OSRM** (internal, optional) — road distance / ETA matrices

External applications should call the **orchestrator only**
(`http://localhost:8080`). The engine and OSRM stay on the private Docker
network.

## Current capabilities

- Orchestrator HTTP API + MySQL persistence
- Same-day route cache (IST) with optional `regenerate: true`
- Fleet totals: waypoint count, demand sum, vehicle count, capacity sum
- `GET /api/v1/routes` returns the **latest** generation (any date); use
  `GET /api/v1/routes/{date}` for a specific day (including today)
- Capacitated vehicle routing via internal route-engine
- Distance providers: Haversine (offline) and OSRM (road network)
- Docker Compose: orchestrator + MySQL + route-engine + OSRM

## Not yet implemented

- Auth / rate limiting
- Alembic migrations (tables are created on orchestrator startup for now)
- Automated / scheduled OSM map refresh for OSRM
- Multi-depot / multi-tenant routing

## Stack

- Python 3.9+
- FastAPI + Uvicorn
- SQLAlchemy 2 + MySQL 8
- Google OR-Tools
- Pydantic
- OSRM (optional; self-host via Docker)

## Architecture

```text
External app
    → orchestrator (:8080)
         → MySQL
         → route-engine (:8000, internal)
              → osrm (:5000, internal)
```

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e .
pip install -e ".[test]"   # for pytest
```

```bash
# Windows
copy .env.sample .env

# macOS / Linux
cp .env.sample .env
```

| Variable | Meaning |
|----------|---------|
| `ROUTE_ENGINE_PROVIDER` | Engine default: `haversine` \| `osrm` |
| `ROUTE_ENGINE_COST` | Engine default: `distance` \| `eta` |
| `OSRM_BASE_URL` | OSRM URL (Compose sets `http://osrm:5000` for the engine) |
| `OSRM_MAP` | Prepared map basename under `osrm-data/` |
| `DATABASE_URL` | SQLAlchemy URL for the orchestrator |
| `ENGINE_BASE_URL` | Route-engine base URL (Compose: `http://route-engine:8000`) |
| `ORCHESTRATOR_TZ` | Calendar day timezone (default `Asia/Kolkata`) |
| `MYSQL_*` | MySQL bootstrap credentials for Compose |

## Orchestrator API (public)

Base URL: `http://localhost:8080`

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Health + DB ping |
| `POST` | `/api/v1/waypoints` | Add waypoints (JSON array) |
| `GET` | `/api/v1/waypoints?active_only=` | List waypoints |
| `GET` | `/api/v1/waypoints/total?active_only=` | Total waypoint count (default active) |
| `GET` | `/api/v1/waypoints/demand/total?active_only=` | Sum of waypoint demand (default active) |
| `PATCH` | `/api/v1/waypoints/{id}` | Update (incl. `is_active`, `is_depot`) |
| `POST` | `/api/v1/vehicles` | Add vehicles (JSON array) |
| `GET` | `/api/v1/vehicles?active_only=` | List vehicles |
| `GET` | `/api/v1/vehicles/total?active_only=` | Total vehicle count (default active) |
| `GET` | `/api/v1/vehicles/capacity/total?active_only=` | Sum of vehicle capacity (default active) |
| `PATCH` | `/api/v1/vehicles/{id}` | Update (incl. `is_active`) |
| `POST` | `/api/v1/routes/generate` | Generate or return today's cached routes |
| `GET` | `/api/v1/routes` | Latest generated route set (any date) |
| `GET` | `/api/v1/routes/{YYYY-MM-DD}` | Latest route for a date (use today for today's) |

Docs: http://localhost:8080/docs

### Generate body

```json
{
  "provider": "osrm",
  "cost_mode": "distance",
  "regenerate": false
}
```

- Uses only DB rows with `is_active=true`.
- Requires exactly one active waypoint with `is_depot=true` (sent to the engine as depot index `0`).
- If a generation already exists for today and `regenerate` is false, returns it with `cached: true`.
- If `regenerate` is true, calls the engine again and stores a new row.

### Totals (dashboard metrics)

All totals default to **active** rows only (`active_only=true`). Pass
`?active_only=false` to include inactive rows.

| Endpoint | Response |
|----------|----------|
| `GET /api/v1/waypoints/total` | `{"total_waypoints": 15, "active_only": true}` |
| `GET /api/v1/waypoints/demand/total` | `{"total_demand": 14, "active_only": true}` |
| `GET /api/v1/vehicles/total` | `{"total_vehicles": 4, "active_only": true}` |
| `GET /api/v1/vehicles/capacity/total` | `{"total_capacity": 14, "active_only": true}` |

### Fetching routes

| Endpoint | Behavior |
|----------|----------|
| `GET /api/v1/routes` | Most recently generated route set (by `generated_at`), **any** service date |
| `GET /api/v1/routes/{YYYY-MM-DD}` | Latest generation for that calendar date (IST). Pass today's date for today's plan |

Both return the same shape as generate (`cached`, `service_date`, `generated_at`,
`was_regenerated`, `provider`, `cost_mode`, `routes`).  
`404` if nothing has been generated yet / nothing for that date.

### Example flow

```bash
# Waypoints (array — one or many)
curl -X POST http://localhost:8080/api/v1/waypoints \
  -H "Content-Type: application/json" \
  -d '[
    {"external_id":"DEPOT","name":"Depot","latitude":8.5241,"longitude":76.9366,"demand":0,"is_depot":true},
    {"name":"Stop A","latitude":8.54,"longitude":76.91}
  ]'

# Vehicles (array — one or many)
curl -X POST http://localhost:8080/api/v1/vehicles \
  -H "Content-Type: application/json" \
  -d '[{"number":"KA01","operator":"Alex","capacity":4}]'

# Dashboard totals
curl http://localhost:8080/api/v1/waypoints/total
curl http://localhost:8080/api/v1/waypoints/demand/total
curl http://localhost:8080/api/v1/vehicles/total
curl http://localhost:8080/api/v1/vehicles/capacity/total

# Generate
curl -X POST http://localhost:8080/api/v1/routes/generate \
  -H "Content-Type: application/json" \
  -d '{"regenerate":false}'

# Latest generation (any date)
curl http://localhost:8080/api/v1/routes

# Today's generation (replace with today's IST date)
curl http://localhost:8080/api/v1/routes/2026-08-25
```

## Run with Docker

Requires Docker Desktop (Linux containers).

```text
Client → orchestrator (:8080) → MySQL
                            → route-engine → osrm
```

### 1. Env file

```bash
copy .env.sample .env   # Windows
cp .env.sample .env     # macOS / Linux
```

### 2. OSRM map data (optional if using Haversine only)

Map extracts and prepared graphs live under `osrm-data/` (gitignored except
`README.md`). Prefer a small region.

#### Download

1. Open [Geofabrik downloads](https://download.geofabrik.de/).
2. Download a `.osm.pbf` into `osrm-data/`.

Example: `osrm-data/southern-zone-260718.osm.pbf` → `OSRM_MAP=southern-zone-260718`.

#### Prepare the graph (one-time per map)

```powershell
$MAP = "southern-zone-260718"
$IMAGE = "ghcr.io/project-osrm/osrm-backend:v5.27.1"
$data = (Resolve-Path .\osrm-data).Path

docker run --rm -t -v "${data}:/data" $IMAGE `
  osrm-extract -p /opt/car.lua "/data/${MAP}.osm.pbf"

docker run --rm -t -v "${data}:/data" $IMAGE `
  osrm-partition "/data/${MAP}.osrm"

docker run --rm -t -v "${data}:/data" $IMAGE `
  osrm-customize "/data/${MAP}.osrm"
```

macOS / Linux: `./scripts/prepare_osrm.sh <map-basename>`

#### Replace / remove existing map data

```powershell
docker compose down
Get-ChildItem .\osrm-data -Exclude README.md | Remove-Item -Recurse -Force
```

Then download, prepare, update `OSRM_MAP`, and start Compose again.

### 3. Start the stack

```bash
docker compose build
docker compose up
```

- Public API: http://localhost:8080/docs
- Engine/OSRM are not published by default (internal network only)

Set `ROUTE_ENGINE_PROVIDER=osrm` in `.env` once map data is ready; otherwise
leave `haversine` for offline distance.

Notes:

- Keep OSRM private — only publish the orchestrator port (`8080`) in production.
- OSRM travel times are profile-based estimates, not live traffic.
- If `docker pull ghcr.io/project-osrm/osrm-backend:...` fails with “denied”,
  try `docker logout ghcr.io` and pull again.

## Route engine (internal)

The engine still exposes `POST /api/v1/routes/generate` for in-network callers
(the orchestrator). Payload shape is unchanged: `waypoints`, `vehicles`,
`depot`, optional `provider` / `cost_mode`.

Local debug (without orchestrator):

```bash
python -m uvicorn route_engine.api.app:app --reload --port 8000
```

## Tests

```bash
pip install -e ".[test]"
python -m pytest
```

## Project layout

```text
src/route_engine/       # Internal CVRP engine + OSRM/Haversine
src/orchestrator/       # Public API + MySQL + engine HTTP client
Dockerfile              # route-engine image
Dockerfile.orchestrator # orchestrator image
docker-compose.yml      # mysql + orchestrator + route-engine + osrm
scripts/prepare_osrm.sh
osrm-data/
tests/
```

## Roadmap

1. Auth / API keys for the orchestrator
2. Alembic migrations
3. Automated OSM refresh pipeline
4. Richer routing constraints as needed
