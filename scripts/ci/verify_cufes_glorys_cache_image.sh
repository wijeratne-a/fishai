#!/usr/bin/env bash
# Fail closed unless the local image ref matches committed rebuild inputs.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

INPUT_HASH="$(scripts/ci/compute_cufes_glorys_cache_key.sh)"
IMAGE="${1:?image ref required}"

got="$(docker image inspect "${IMAGE}" --format '{{index .Config.Labels "fishai.cufes_glorys.cache_key"}}' 2>/dev/null || true)"
if [[ "${got}" != "${INPUT_HASH}" ]]; then
  echo "CUFES×GLORYS cache image label mismatch: expected ${INPUT_HASH}, got ${got:-<empty>}" >&2
  exit 1
fi

echo "Verified cache image ${IMAGE} (fishai.cufes_glorys.cache_key=${INPUT_HASH})"
