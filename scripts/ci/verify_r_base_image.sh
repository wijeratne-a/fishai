#!/usr/bin/env bash
# Fail closed unless the local image ref matches committed inputs.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

INPUT_HASH="$(scripts/ci/compute_r_base_image_ref.sh)"
IMAGE="${1:?image ref required}"

got="$(docker image inspect "${IMAGE}" --format '{{index .Config.Labels "fishai.r_base.input_hash"}}')"
if [[ "${got}" != "${INPUT_HASH}" ]]; then
  echo "R base image label mismatch: expected ${INPUT_HASH}, got ${got:-<empty>}" >&2
  exit 1
fi

echo "Verified R base image ${IMAGE} (fishai.r_base.input_hash=${INPUT_HASH})"
