#!/usr/bin/env bash
# Offshore sardine and anchovy egg and spawning-habitat pilot — official spatial-block CV dry-run (egg encounter; lead 0 only; EVIDENCE ONLY — NOT FOR DISPLAY).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

export FISHAI_ROOT="$ROOT"
export RENV_PATHS_LIBRARY="${RENV_PATHS_LIBRARY:-$ROOT/renv/library}"

if [[ ! -f "$ROOT/data/processed/calcofi_cufes/cufes_training_covariates.parquet" ]]; then
  echo "Missing training table; run staging/cv-real-run/build_bot2_training_table.sh first" >&2
  exit 1
fi

export R_LIBS="${R_LIBS:-$ROOT/renv/library}"
export RENV_PATHS_LIBRARY="${RENV_PATHS_LIBRARY:-$ROOT/renv/library}"

python3 "$ROOT/staging/cv-real-run/patch_source_product_myint.py"
python3 "$ROOT/staging/cv-real-run/enrich_events_dist_shore_km.py"

if [[ ! -f "$ROOT/staging/cv-real-run/artifacts/scb_pilot_land_sf.rds" ]]; then
  Rscript staging/cv-real-run/build_scb_pilot_land_sf.R
fi

# Coarser mesh fallback: pass --mesh-cutoff-km 12 (or 15) before --out-dir.
Rscript scripts/models/cufes_real_spatial_cv_staging.R \
  --species both \
  --out-dir "$ROOT/staging/cv-real-run/dry-run"
