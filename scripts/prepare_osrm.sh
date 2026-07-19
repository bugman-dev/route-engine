#!/usr/bin/env bash
# One-time MLD preprocessing for a private OSRM instance.
#
# Usage:
#   ./scripts/prepare_osrm.sh <map-basename>
#
# Place <map-basename>.osm.pbf in ./osrm-data first, e.g.:
#   osrm-data/kerala-latest.osm.pbf
#   ./scripts/prepare_osrm.sh kerala-latest
#
# Then set OSRM_MAP=kerala-latest in .env and run: docker compose up

set -euo pipefail

MAP="${1:-}"
if [[ -z "${MAP}" ]]; then
  echo "Usage: $0 <map-basename>" >&2
  echo "Example: $0 kerala-latest" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${ROOT}/osrm-data"
PBF="${DATA_DIR}/${MAP}.osm.pbf"
IMAGE="ghcr.io/project-osrm/osrm-backend:v5.27.1"

if [[ ! -f "${PBF}" ]]; then
  echo "Missing map file: ${PBF}" >&2
  echo "Download a regional extract (e.g. from Geofabrik) into osrm-data/." >&2
  exit 1
fi

echo "Using image ${IMAGE}"
echo "Extracting ${MAP}.osm.pbf ..."
docker run --rm -t \
  -v "${DATA_DIR}:/data" \
  "${IMAGE}" \
  osrm-extract -p /opt/car.lua "/data/${MAP}.osm.pbf"

echo "Partitioning ..."
docker run --rm -t \
  -v "${DATA_DIR}:/data" \
  "${IMAGE}" \
  osrm-partition "/data/${MAP}.osrm"

echo "Customizing ..."
docker run --rm -t \
  -v "${DATA_DIR}:/data" \
  "${IMAGE}" \
  osrm-customize "/data/${MAP}.osrm"

echo
echo "Done. Set OSRM_MAP=${MAP} in .env, then:"
echo "  docker compose up"
