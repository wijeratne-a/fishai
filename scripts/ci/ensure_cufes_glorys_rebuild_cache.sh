#!/usr/bin/env bash
# Pull the CUFES×GLORYS rebuild cache when present and verified; optionally extract or publish.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

INPUT_HASH="$(scripts/ci/compute_cufes_glorys_cache_key.sh)"
REGISTRY="${FISHAI_CUFES_GLORYS_REGISTRY:-ghcr.io/wijeratne-a/fishai/cufes-glorys-rebuild}"
IMAGE="${FISHAI_CUFES_GLORYS_CACHE_IMAGE:-${REGISTRY}:${INPUT_HASH}}"
ARCHIVE="${FISHAI_CUFES_GLORYS_ARCHIVE:-data/cache/cufes_glorys_rebuild_${INPUT_HASH}.tar.gz}"

label_ok() {
  local img="$1"
  local got
  got="$(docker image inspect "${img}" --format '{{index .Config.Labels "fishai.cufes_glorys.cache_key"}}' 2>/dev/null || true)"
  [[ "${got}" == "${INPUT_HASH}" ]]
}

extract_archive() {
  mkdir -p "$(dirname "${ARCHIVE}")"
  local container
  container="$(docker create "${IMAGE}")"
  trap 'docker rm -f "${container}" >/dev/null 2>&1 || true' RETURN
  docker cp "${container}:/artifact.tar.gz" "${ARCHIVE}"
  python - <<PY
from pathlib import Path
from fishai.ingestion.rebuild.cufes_glorys_artifact_cache import restore_cache_archive

restore_cache_archive(Path("${ARCHIVE}"))
PY
  echo "Restored CUFES×GLORYS rebuild artifacts from ${IMAGE}"
}

if docker pull "${IMAGE}" 2>/dev/null && label_ok "${IMAGE}"; then
  echo "Using cached CUFES×GLORYS rebuild image ${IMAGE}"
  if [[ "${EXTRACT:-0}" == "1" ]]; then
    extract_archive
  fi
  exit 0
fi

if [[ "${PUBLISH:-0}" == "1" ]]; then
  echo "Cache image missing; publishing from local archive ${ARCHIVE}"
  PUSH=1 FISHAI_CUFES_GLORYS_CACHE_IMAGE="${IMAGE}" FISHAI_CUFES_GLORYS_ARCHIVE="${ARCHIVE}" \
    scripts/ci/build_cufes_glorys_cache_image.sh
  exit 0
fi

echo "CUFES×GLORYS rebuild cache miss for ${IMAGE} (cold rebuild required)" >&2
exit 1
