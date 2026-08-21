# Route Engine Admin — App Description & User Flow

A web admin for **fleet and stop management** and **daily route generation**. Operators configure the depot, stops, and vehicles, then generate and review optimized routes for **today (IST)**.

**Backend:** orchestrator at `http://localhost:8080`  
**No auth today** — treat as internal admin only.

---

## App purpose

| Role | Goal |
|------|------|
| **Ops admin** | Keep waypoints and vehicles up to date |
| **Dispatcher** | Generate today's routes and assign stops per vehicle |
| **Viewer** | Review cached routes and route metadata |

Core loop:

```text
Setup fleet → Validate readiness → Generate routes → Review per-vehicle plans
```

---

## Information architecture (suggested pages)

```text
┌─────────────────────────────────────────────────────────┐
│  Sidebar / Top nav                                       │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ Dashboard│ Waypoints│ Vehicles │ Routes   │ Settings*   │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
* Settings = client-side defaults only (provider, cost_mode); no backend settings API yet
```

### 1. Dashboard (home)

Overview and "ready to generate?" status.

**Shows:**

- Service date (IST, from client clock or first route response)
- Counts: active waypoints (`GET /api/v1/waypoints/total`), depot configured?
- Fleet capacity vs total demand (`GET /api/v1/vehicles/capacity/total`, `GET /api/v1/waypoints/demand/total`)
- Today's route status: not generated / cached / last generated at
- System health (`GET /health`)
- Primary CTA: **Generate routes**

**Readiness checks** (mirror backend rules):

- ≥ 1 active waypoint
- Exactly 1 active depot (`is_depot: true`)
- ≥ 1 active vehicle
- Total demand ≤ total fleet capacity (warn if not; use the totals APIs above)

---

### 2. Waypoints

Manage stops and depot.

**List view**

- Table: name, external_id, lat/lng, demand, depot badge, active toggle
- Filters: All / Active only (`GET /api/v1/waypoints?active_only=true`)
- Map preview (optional): pins for all active waypoints, depot highlighted

**Actions**

- **Add waypoints** — form or JSON paste; submits array to `POST /api/v1/waypoints`
- **Edit** — `PATCH /api/v1/waypoints/{id}`
- **Deactivate** — set `is_active: false` via PATCH (no DELETE API)

**Depot rule (important UX)**

- Only one active depot allowed
- When marking a waypoint as depot, warn: "Another depot is already active" or auto-unset the other (would need PATCH on the old depot — backend does not do this automatically)

**Fields**

| Field | Required | Notes |
|-------|----------|-------|
| name | yes | Display name |
| latitude | yes | |
| longitude | yes | |
| demand | no (default 1) | 0 for depot |
| external_id | no | Unique if set |
| is_depot | no | Only one active |
| is_active | no | Default true |

---

### 3. Vehicles

Manage fleet.

**List view**

- Table: number, operator, capacity, external_id, active toggle
- Filter: All / Active only

**Actions**

- **Add vehicles** — array to `POST /api/v1/vehicles`
- **Edit** — `PATCH /api/v1/vehicles/{id}`
- **Deactivate** — `is_active: false`

**Fields**

| Field | Required | Notes |
|-------|----------|-------|
| number | yes | Plate / fleet number |
| operator | yes | Driver name |
| capacity | yes | > 0 |
| external_id | no | Unique if set |
| is_active | no | Default true |

**Errors to surface**

- `409` on duplicate `external_id`

---

### 4. Routes (main dispatcher screen)

Generate and view today's plan.

**Generate panel**

- Provider: `osrm` | `haversine` (optional; falls back to server env)
- Cost mode: `distance` | `eta`
- Regenerate toggle:
  - `false` — use cache if today already has routes
  - `true` — force new solve

**API:** `POST /api/v1/routes/generate`

```json
{
  "provider": "osrm",
  "cost_mode": "distance",
  "regenerate": false
}
```

**Response metadata to show**

- `cached` — returned from cache vs fresh solve
- `service_date`
- `generated_at`
- `was_regenerated`
- `provider`, `cost_mode`

**Route cards (one per vehicle)**

Each item in `routes[]`:

| Field | UI use |
|-------|--------|
| `vehicle_number` | Card title |
| `operator` | Subtitle |
| `capacity` | Badge |
| `stops` | Ordered list (depot → stops → depot) |
| `total_distance_km` | Summary (OSRM / Haversine) |
| `total_duration_seconds` | ETA summary (mainly OSRM) |
| `leg_distances_km` | Per-leg breakdown |
| `etas_seconds` | Arrival time per stop |
| `cost_mode` | What was optimized |

**Layout ideas**

- Left: vehicle route list
- Right: map with colored polylines per vehicle
- Expandable row: stop sequence + leg distance/duration

**History**

- Today: `GET /api/v1/routes`
- Specific date: `GET /api/v1/routes/{YYYY-MM-DD}`
- No "list all dates" API — v1 can use a date picker only

---

### 5. Settings (client-side, optional)

Store UI defaults in localStorage:

- Default provider
- Default cost_mode
- API base URL (`http://localhost:8080`)

---

## Primary user flows

### Flow A — First-time setup

```text
1. Open Dashboard → health check
2. Waypoints → add depot + stops (bulk array)
3. Vehicles → add fleet (bulk array)
4. Dashboard → readiness turns green
5. Routes → Generate
6. Review per-vehicle stop order
```

### Flow B — Daily dispatch (returning user)

```text
1. Dashboard → "Routes already generated today" (cached)
2. Routes → view today's plan
3. Optional: deactivate a vehicle / waypoint → Regenerate (regenerate: true)
```

### Flow C — Fleet change mid-day

```text
1. Vehicles or Waypoints → PATCH is_active / edit fields
2. Routes → Regenerate with regenerate: true
3. Confirm new plan vs old (show generated_at)
```

### Flow D — Troubleshooting failed generate

```text
1. Generate fails (400)
2. Show API detail, e.g.:
   - No active waypoints
   - No active vehicles
   - No depot / multiple depots
3. Link user to Waypoints or Vehicles to fix
```

**502** = engine/OSRM unreachable — show retry + health status.

---

## API map (for frontend integration)

| Screen action | Method | Endpoint |
|---------------|--------|----------|
| Health | GET | `/health` |
| List waypoints | GET | `/api/v1/waypoints?active_only=` |
| Total waypoints | GET | `/api/v1/waypoints/total?active_only=` |
| Total demand | GET | `/api/v1/waypoints/demand/total?active_only=` |
| Create waypoints | POST | `/api/v1/waypoints` (array) |
| Update waypoint | PATCH | `/api/v1/waypoints/{id}` |
| List vehicles | GET | `/api/v1/vehicles?active_only=` |
| Total capacity | GET | `/api/v1/vehicles/capacity/total?active_only=` |
| Create vehicles | POST | `/api/v1/vehicles` (array) |
| Update vehicle | PATCH | `/api/v1/vehicles/{id}` |
| Generate routes | POST | `/api/v1/routes/generate` |
| Today's routes | GET | `/api/v1/routes` |
| Routes by date | GET | `/api/v1/routes/{date}` |

OpenAPI: http://localhost:8080/docs

---

## Validation & error UX

| Condition | HTTP | User message |
|-----------|------|--------------|
| Duplicate external_id | 409 | "ID already exists" |
| No depot / multiple depots | 400 | Fix depot in Waypoints |
| No active fleet | 400 | Add or activate vehicles |
| Insufficient capacity | 400/502 | "Fleet capacity too low for demand" |
| No route for date | 404 | "No routes for this date — generate first" |
| Engine down | 502 | "Routing service unavailable" |

**Pre-flight on Generate button**

- Block or warn if readiness checks fail
- Confirm dialog when `regenerate: true` ("This will create a new plan for today")

---

## Suggested UI components

1. **Readiness banner** — dashboard + routes page
2. **Data table** — waypoints / vehicles with inline active toggle
3. **Bulk import modal** — paste JSON array
4. **Map component** — Leaflet / Mapbox / Google Maps
5. **Route timeline** — stops with distance/duration chips
6. **Generate drawer** — provider, cost_mode, regenerate
7. **Toast notifications** — success / 409 / 400 / 502
8. **Empty states** — "No waypoints yet", "No routes for today"

---

## MVP vs later

### MVP (matches current API)

- CRUD via list + PATCH (no delete)
- Bulk create via array POST
- Generate + view today
- Date picker for historical day
- Map + route list

### V2 (needs backend work)

- Auth / roles
- Delete endpoints
- Route history list
- CSV import/export
- Multi-depot / multi-tenant
- Live tracking

---

## One-line product description

> **Route Engine Admin** is an internal operations console to manage depots, pickup stops, and vehicle fleets, then generate and review optimized daily delivery/pickup routes powered by the route-engine orchestrator.
