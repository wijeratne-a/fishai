"""Repo immutability helpers shared by conftest and explicit policy tests."""

from __future__ import annotations

import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_DIR = REPO_ROOT / "data" / "provenance"

_SESSION_PROVENANCE_HASHES: dict[Path, str] | None = None


def provenance_file_hashes() -> dict[Path, str]:
    out: dict[Path, str] = {}
    if not PROVENANCE_DIR.is_dir():
        return out
    for path in sorted(PROVENANCE_DIR.rglob("*")):
        if path.is_file():
            rel = path.relative_to(REPO_ROOT)
            out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def set_session_provenance_baseline(hashes: dict[Path, str]) -> None:
    global _SESSION_PROVENANCE_HASHES
    _SESSION_PROVENANCE_HASHES = dict(hashes)


def session_provenance_baseline() -> dict[Path, str]:
    if _SESSION_PROVENANCE_HASHES is None:
        raise RuntimeError("provenance baseline not initialized (pytest session not started)")
    return dict(_SESSION_PROVENANCE_HASHES)
