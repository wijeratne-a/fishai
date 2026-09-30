#!/usr/bin/env bash
# Restore durable cache or run the cold CUFES×GLORYS rebuild once, then optionally publish GHCR cache.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

INPUT_HASH="$(scripts/ci/compute_cufes_glorys_cache_key.sh)"
ARCHIVE="${FISHAI_CUFES_GLORYS_ARCHIVE:-data/cache/cufes_glorys_rebuild_${INPUT_HASH}.tar.gz}"

if [[ "${SKIP_CACHE:-0}" != "1" ]]; then
  if EXTRACT=1 scripts/ci/ensure_cufes_glorys_rebuild_cache.sh; then
    python - <<'PY'
from fishai.ingestion.rebuild.cufes_glorys_artifact_cache import assert_cufes_glorys_rebuild_guards

assert_cufes_glorys_rebuild_guards()
print("CUFES×GLORYS rebuild: cache hit (skipped ERDDAP and GLORYS cold downloads)")
PY
    exit 0
  fi
fi

echo "CUFES×GLORYS rebuild: cache miss; running cold builders"
python - <<PY
from pathlib import Path
from fishai.ingestion.rebuild.cufes_glorys_artifact_cache import run_cufes_glorys_rebuild

run_cufes_glorys_rebuild(
    skip_cache=True,
    publish_cache=${PUBLISH_CACHE:-0},
    archive_path=Path("${ARCHIVE}"),
)
print("CUFES×GLORYS rebuild: cold path complete")
PY

if [[ "${PUBLISH_CACHE:-0}" == "1" ]]; then
  PUSH=1 FISHAI_CUFES_GLORYS_ARCHIVE="${ARCHIVE}" scripts/ci/build_cufes_glorys_cache_image.sh
fi
