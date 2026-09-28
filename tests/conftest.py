"""Shared pytest hooks (provenance / artifacts immutability, test log isolation)."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

import pytest

from tests.repo_guards import PROVENANCE_DIR, set_session_provenance_baseline

REPO_ROOT = Path(__file__).resolve().parents[1]
_TRACKED_PREFIXES = (
    PROVENANCE_DIR,
    REPO_ROOT / "artifacts",
)

_PHYSICS_TEST_DIR = Path(__file__).resolve().parent / "ingestion" / "physics"
if str(_PHYSICS_TEST_DIR) not in sys.path:
    sys.path.insert(0, str(_PHYSICS_TEST_DIR))


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


def _tree_snapshot(root: Path) -> dict[str, tuple[int, int]]:
    if not root.is_dir():
        return {}
    return {
        str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }


def _redirect_pull_logs_in_config(cfg: dict[str, Any], tmp: Path) -> dict[str, Any]:
    out = dict(cfg)
    pl = dict(out.get("pull_logs") or {})
    wcofs = str(pl.get("wcofs", ""))
    glorys = str(pl.get("glorys", ""))
    if wcofs.startswith("data/provenance"):
        pl["wcofs"] = str(tmp / "wcofs_pull_log.jsonl")
    if glorys.startswith("data/provenance"):
        pl["glorys"] = str(tmp / "copernicus_pull_log.jsonl")
    out["pull_logs"] = pl
    cov = dict(out.get("coverage_report") or {})
    jp = str(cov.get("json_path", ""))
    cp = str(cov.get("csv_path", ""))
    if jp.startswith("artifacts/"):
        cov["json_path"] = str(tmp / "coverage_report.json")
    if cp.startswith("artifacts/"):
        cov["csv_path"] = str(tmp / "coverage_cells.csv")
    if cov:
        out["coverage_report"] = cov
    return out


@pytest.fixture(autouse=True)
def _isolate_pull_logs_and_harmonization_outputs(tmp_path: Path) -> None:
    """
    Tests that load overlap config or call overlap pairing must not write under
    ``data/provenance/`` or committed ``artifacts/harmonization/`` paths.
    """
    import fishai.ingestion.physics.wcofs_glorys_overlap as overlap_mod

    original = overlap_mod.load_overlap_config

    def _wrapped(path: Path | str | None = None) -> dict[str, Any]:
        cfg = original(path)
        return _redirect_pull_logs_in_config(cfg, tmp_path)

    overlap_mod.load_overlap_config = _wrapped  # type: ignore[method-assign]
    yield
    overlap_mod.load_overlap_config = original  # type: ignore[method-assign]


@pytest.fixture(scope="session", autouse=True)
def _provenance_and_artifacts_unchanged_by_tests() -> None:
    before = _tracked_repo_files()
    set_session_provenance_baseline(
        {rel: digest for rel, digest in before.items() if str(rel).startswith("data/provenance/")}
    )
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


@pytest.fixture
def repo_provenance_snapshot() -> dict[str, tuple[int, int]]:
    """Snapshot of committed provenance files for per-test assertions."""
    root = REPO_ROOT / "data" / "provenance"
    return _tree_snapshot(root)
