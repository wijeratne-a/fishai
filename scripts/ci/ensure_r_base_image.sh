#!/usr/bin/env bash
# Pull the R base image when present and verified; otherwise build and push (fail closed on stale labels).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

INPUT_HASH="$(scripts/ci/compute_r_base_image_ref.sh)"
REGISTRY="${FISHAI_R_BASE_REGISTRY:-ghcr.io/wijeratne-a/fishai/r-env}"
IMAGE="${REGISTRY}:${INPUT_HASH}"

label_ok() {
  local img="$1"
  local got
  got="$(docker image inspect "${img}" --format '{{index .Config.Labels "fishai.r_base.input_hash"}}' 2>/dev/null || true)"
  [[ "${got}" == "${INPUT_HASH}" ]]
}

if docker pull "${IMAGE}" 2>/dev/null && label_ok "${IMAGE}"; then
  echo "Using cached R base image ${IMAGE}"
  exit 0
fi

echo "R base image missing or stale; building and publishing ${IMAGE}"
PUSH=1 FISHAI_R_BASE_IMAGE="${IMAGE}" scripts/ci/build_r_base_image.sh

if ! label_ok "${IMAGE}"; then
  echo "Built image label does not match input hash ${INPUT_HASH}" >&2
  exit 1
fi
