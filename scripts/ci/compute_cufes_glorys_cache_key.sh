#!/usr/bin/env bash
# Print immutable GHCR tag for the CUFES × GLORYS rebuild artifact cache.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

python3 - <<'PY'
from fishai.ingestion.rebuild.cufes_glorys_artifact_cache import compute_cache_key

print(compute_cache_key())
PY
