#!/usr/bin/env bash
# Build and optionally push the R base image. Requires docker and (for push) registry login.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

INPUT_HASH="$(scripts/ci/compute_r_base_image_ref.sh)"
IMAGE="${FISHAI_R_BASE_IMAGE:-ghcr.io/wijeratne-a/fishai/r-env:${INPUT_HASH}}"

echo "Building R base image ${IMAGE}"
docker build \
  -f docker/Dockerfile.r-base \
  --build-arg "FISHAI_R_BASE_INPUT_HASH=${INPUT_HASH}" \
  -t "${IMAGE}" \
  .

if [[ "${PUSH:-0}" == "1" ]]; then
  echo "Pushing ${IMAGE}"
  docker push "${IMAGE}"
fi

echo "${IMAGE}"
