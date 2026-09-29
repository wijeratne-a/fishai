#!/usr/bin/env bash
# Build PR #15 table @ pin, blank bogus upwelling (794261b), run #5 split audit at current HEAD.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
HEAD_SHA="$(git rev-parse HEAD)"
PR15_REF="${PR15_PIN_REF:-794261bfb0cd86ce72145190a1b564ea85202865}"
OUT_DIR="${1:-/tmp/pr15_audit_at_head}"
export FISHAI_ROOT="$ROOT"
export PR15_PIN_REF="$PR15_REF"

python3 scripts/models/run_pr15_ocean_dry_run_audit.py --ref "$PR15_REF" --out-dir "$OUT_DIR"

python3 << PY
import pandas as pd
from pathlib import Path
out = Path("$OUT_DIR")
cov = pd.read_parquet(out / "cufes_training_covariates.parquet")
if "upwelling" in cov.columns:
    cov["upwelling"] = ""
if "upwelling_status" not in cov.columns:
    cov["upwelling_status"] = "no_consistent_wind_product"
else:
    cov["upwelling_status"] = "no_consistent_wind_product"
csv_dir = out / "csv_for_r"
csv_dir.mkdir(exist_ok=True)
cov.to_csv(csv_dir / "cufes_training_covariates.csv", index=False)
pd.read_parquet(out / "cufes_training_covariate_drops.parquet").to_csv(
    csv_dir / "cufes_training_covariate_drops.csv", index=False
)
events_p = Path("$ROOT/data/processed/calcofi_cufes/cufes_events.parquet")
counts_p = Path("$ROOT/data/processed/calcofi_cufes/cufes_counts.parquet")
pd.read_parquet(events_p).to_csv(csv_dir / "cufes_events.csv", index=False)
pd.read_parquet(counts_p).to_csv(csv_dir / "cufes_counts.csv", index=False)
PY

COV_CSV="$OUT_DIR/csv_for_r/cufes_training_covariates.csv"
DROPS_CSV="$OUT_DIR/csv_for_r/cufes_training_covariate_drops.csv"
AUDIT_JSON="$OUT_DIR/fishai_split_audit_at_head.json"

FISHAI_ROOT="$ROOT" Rscript scripts/models/pr15_fishai_split_audit.R \
  --covariates "$COV_CSV" \
  --drops "$DROPS_CSV" \
  --head-sha "$HEAD_SHA" \
  --out "$AUDIT_JSON"

python3 << PY
import json
from pathlib import Path
head = "$HEAD_SHA"
audit = json.loads(Path("$AUDIT_JSON").read_text())
audit["fishai_head_sha"] = head
sys_path = Path("$ROOT/src")
import sys
sys.path.insert(0, str(sys_path))
from fishai.models.bot2_covariate_schema import compare_bot2_to_sdmtmb, mismatches_as_dicts
audit["schema_mismatches_pr5_vs_pr15"] = mismatches_as_dicts(
    compare_bot2_to_sdmtmb(ref="$PR15_REF")
)
Path("$AUDIT_JSON").write_text(json.dumps(audit, indent=2) + "\\n")
print(json.dumps(audit, indent=2))
PY
