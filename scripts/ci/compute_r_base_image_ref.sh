#!/usr/bin/env bash
# Print immutable GHCR tag for the R base image from committed inputs.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MANIFEST="${ROOT}/scripts/ci/r_base_image_input_paths.txt"

if [[ ! -f "${MANIFEST}" ]]; then
  echo "missing manifest: ${MANIFEST}" >&2
  exit 1
fi

{
  while IFS= read -r relpath || [[ -n "${relpath}" ]]; do
    relpath="${relpath%%#*}"
    relpath="$(echo -n "${relpath}" | xargs)"
    [[ -z "${relpath}" ]] && continue
    path="${ROOT}/${relpath}"
    if [[ ! -f "${path}" ]]; then
      echo "missing input file: ${relpath}" >&2
      exit 1
    fi
    sha256sum "${path}"
  done < "${MANIFEST}"
} | sha256sum | awk '{print $1}'
