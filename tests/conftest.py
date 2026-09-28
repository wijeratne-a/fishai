"""Pytest configuration: allow imports of co-located test helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from fishai.ingestion.sources import REPO_ROOT

_PHYSICS_TEST_DIR = Path(__file__).resolve().parent / "ingestion" / "physics"
if str(_PHYSICS_TEST_DIR) not in sys.path:
    sys.path.insert(0, str(_PHYSICS_TEST_DIR))

_GUARD_ROOTS = (
    REPO_ROOT / "data" / "provenance",
    REPO_ROOT / "artifacts",
)


def _tree_snapshot(root: Path) -> dict[str, tuple[int, int]]:
    if not root.is_dir():
        return {}
    return {
        str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }


@pytest.fixture(scope="session", autouse=True)
def _guard_repo_provenance_and_artifacts() -> None:
    before = {str(root): _tree_snapshot(root) for root in _GUARD_ROOTS}
    yield
    after = {str(root): _tree_snapshot(root) for root in _GUARD_ROOTS}
    assert before == after, "Test run modified data/provenance or artifacts/"


@pytest.fixture
def repo_provenance_snapshot() -> dict[str, tuple[int, int]]:
    """Snapshot of committed provenance files for per-test assertions."""
    root = REPO_ROOT / "data" / "provenance"
    return _tree_snapshot(root)
