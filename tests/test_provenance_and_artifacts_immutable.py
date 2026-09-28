"""Ensure pytest never mutates repo ``data/provenance`` or ``artifacts``."""

from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
_TRACKED_PREFIXES = (
    REPO_ROOT / "data" / "provenance",
    REPO_ROOT / "artifacts",
)


def _tracked_repo_files() -> dict[Path, str]:
    out: dict[Path, str] = {}
    for base in _TRACKED_PREFIXES:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file():
                rel = path.relative_to(REPO_ROOT)
                out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


@pytest.fixture(scope="session", autouse=True)
def _provenance_and_artifacts_unchanged_by_tests() -> None:
    before = _tracked_repo_files()
    yield
    after = _tracked_repo_files()
    if before.keys() != after.keys():
        added = set(after) - set(before)
        removed = set(before) - set(after)
        msg = []
        if added:
            msg.append("new files: " + ", ".join(str(p) for p in sorted(added)))
        if removed:
            msg.append("removed files: " + ", ".join(str(p) for p in sorted(removed)))
        pytest.fail("data/provenance or artifacts tree changed during tests: " + "; ".join(msg))
    changed = [rel for rel in before if before[rel] != after[rel]]
    if changed:
        pytest.fail(
            "data/provenance or artifacts file content changed during tests: "
            + ", ".join(str(p) for p in sorted(changed))
        )


def test_provenance_immutability_hook_is_registered() -> None:
    src = inspect.getsource(_provenance_and_artifacts_unchanged_by_tests)
    assert "data/provenance" in src
    assert "pytest.fail" in src
