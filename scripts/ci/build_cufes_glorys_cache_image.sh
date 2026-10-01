#!/usr/bin/env bash
# Build and optionally push the GHCR cache image from a local tarball (requires docker + login).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

INPUT_HASH="$(scripts/ci/compute_cufes_glorys_cache_key.sh)"
REGISTRY="${FISHAI_CUFES_GLORYS_REGISTRY:-ghcr.io/wijeratne-a/fishai/cufes-glorys-rebuild}"
IMAGE="${FISHAI_CUFES_GLORYS_CACHE_IMAGE:-${REGISTRY}:${INPUT_HASH}}"
ARCHIVE="${FISHAI_CUFES_GLORYS_ARCHIVE:-data/cache/cufes_glorys_rebuild_${INPUT_HASH}.tar.gz}"

if [[ ! -f "${ARCHIVE}" ]]; then
  echo "missing cache archive: ${ARCHIVE}" >&2
  exit 1
fi

STAGING="${ROOT}/.cache/docker_staging_${INPUT_HASH}"
rm -rf "${STAGING}"
mkdir -p "${STAGING}"
cp "${ARCHIVE}" "${STAGING}/artifact.tar.gz"

echo "Building CUFES×GLORYS cache image ${IMAGE}"
docker build \
  -f docker/Dockerfile.cufes-glorys-cache \
  --build-arg "FISHAI_CUFES_GLORYS_CACHE_KEY=${INPUT_HASH}" \
  -t "${IMAGE}" \
  "${STAGING}"
rm -rf "${STAGING}"

if [[ "${PUSH:-0}" == "1" ]]; then
  echo "Pushing ${IMAGE}"
  docker push "${IMAGE}"
fi

echo "${IMAGE}"
