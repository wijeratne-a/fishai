#!/usr/bin/env bash
# Build PR #28 CUFES training covariates into this repo's data/processed (local only).
# Run from repo root; uses a read-only clone of cursor/real-training-table-evidence for bot2 code.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PR28_ROOT="${PR28_ROOT:-/tmp/fishai-pr28}"
DATA_ROOT="${DATA_ROOT:-$ROOT}"

if [[ ! -d "$PR28_ROOT/src/fishai/ingestion/physics" ]]; then
  echo "PR28 clone missing at $PR28_ROOT; set PR28_ROOT or shallow-clone cursor/real-training-table-evidence" >&2
  exit 1
fi

pip install -q -e "$PR28_ROOT"
cd "$PR28_ROOT"

echo "== CUFES biology sync (ERDDAP) =="
fishai-bio sync cufes --start 1996-01-01 --end 2022-04-27

mkdir -p "$DATA_ROOT/data/processed/calcofi_cufes"
mkdir -p "$DATA_ROOT/data/derived/physics" "$DATA_ROOT/data/derived/manifests"
mkdir -p "$DATA_ROOT/data/cache/glorys_cufes"

if [[ ! -d "$DATA_ROOT/data/derived/physics/wcofs_h_glorys_pilot.zarr" ]]; then
  echo "== WCOFS h on GLORYS grid (one ROMS export) =="
  python3 "$ROOT/staging/cv-real-run/export_wcofs_h_glorys_pilot.py" \
    --repo-root "$PR28_ROOT" \
    --artifact "$DATA_ROOT/data/derived/physics/wcofs_h_glorys_pilot.zarr" \
    --manifest "$DATA_ROOT/data/derived/manifests/wcofs_h_glorys_grid.json"
fi

echo "== GLORYS training covariates (live Copernicus) =="
fishai-physics build-cufes-training-covariates \
  --output "$PR28_ROOT/data/processed/calcofi_cufes/cufes_training_covariates.parquet"

echo "== Copy processed tables to workspace =="
rsync -a "$PR28_ROOT/data/processed/calcofi_cufes/" "$DATA_ROOT/data/processed/calcofi_cufes/"
rsync -a "$PR28_ROOT/data/derived/" "$DATA_ROOT/data/derived/" 2>/dev/null || true

echo "Training table build complete under $DATA_ROOT/data/processed/calcofi_cufes/"
