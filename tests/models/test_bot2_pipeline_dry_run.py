"""Bot2 covariate schema vs PR #5 and end-to-end dry-run pipeline (temp outputs only)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from fishai.models.bot2_covariate_schema import (
    compare_bot2_to_sdmtmb,
    mismatches_as_dicts,
)
from fishai.models.bot2_expected_contract import (
    expected_training_output_columns,
    harness_run_metadata,
    resolve_bot2_schema_mode,
)

_TEST_DIR = Path(__file__).resolve().parent
if str(_TEST_DIR) not in sys.path:
    sys.path.insert(0, str(_TEST_DIR))
from bot2_spring_subset_fixtures import write_spring_subset_csvs

REPO = Path(__file__).resolve().parents[2]
DRY_RUN_R = REPO / "scripts" / "models" / "cufes_pipeline_dry_run.R"
BOT2_BRANCH = "origin/cursor/cufes-glorys-training-covariates-faff"


@pytest.fixture(scope="module", autouse=True)
def _fetch_bot2_branch_for_schema_tests() -> None:
    subprocess.run(
        ["git", "fetch", "origin", "cursor/cufes-glorys-training-covariates-faff"],
        cwd=REPO,
        check=False,
        capture_output=True,
    )


def test_bot2_schema_mismatch_report_is_stable() -> None:
    result = compare_bot2_to_sdmtmb(ref=BOT2_BRANCH)
    if not result.bot2_columns:
        pytest.skip("bot2 branch schema not available in this checkout")
    mismatches = mismatches_as_dicts(result)
    kinds = {m["kind"] for m in mismatches}
    # Production YAML on this branch already points at calcofi_cufes training parquets
    # and maps log_depth to bottom_depth_m; bot2 vs sdmTMB diff is depth naming only.
    assert kinds == {"depth_column_name"}


def test_bot2_branch_training_columns_include_source_product() -> None:
    result = compare_bot2_to_sdmtmb(ref=BOT2_BRANCH)
    if not result.bot2_columns:
        pytest.skip("bot2 branch schema not available in this checkout")
    assert "source_product" in result.bot2_columns


def test_expected_contract_columns_cover_pr4_and_covariates() -> None:
    cols = expected_training_output_columns()
    for name in ("time", "lat", "lon", "stop_lat", "stop_lon"):
        assert name not in cols  # events table, not covariate output
    assert "event_id" in cols
    assert "source_product" in cols
    assert "upwelling_status" in cols
    meta = harness_run_metadata()
    assert meta["mode"] in ("expected", "git")
    assert isinstance(meta["branch_existed"], bool)


def test_bot2_schema_mode_auto_resolves() -> None:
    mode = resolve_bot2_schema_mode("auto")
    assert mode in ("expected", "git")


@pytest.mark.skipif(shutil.which("Rscript") is None, reason="Rscript required (docker-r job)")
@pytest.mark.parametrize("species", ["sardine", "anchovy"])
def test_cufes_pipeline_dry_run_stages(tmp_path: Path, species: str) -> None:
    paths = write_spring_subset_csvs(tmp_path / "inputs")
    assert paths["mode"] in ("expected", "git")
    assert isinstance(paths["branch_existed"], bool)
    out_dir = tmp_path / "dry_run" / species
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "Rscript",
        str(DRY_RUN_R),
        "--out-dir",
        str(out_dir),
        "--events",
        str(paths["events"]),
        "--counts",
        str(paths["counts"]),
        "--covariates",
        str(paths["covariates"]),
        "--species",
        species,
    ]
    proc = subprocess.run(
        cmd,
        cwd=REPO,
        env={
            **os.environ,
            "FISHAI_ROOT": str(REPO),
            "RENV_PATHS_LIBRARY": str(REPO / "renv" / "library"),
            "FISHAI_GLORYS_PINNED_CATALOG_JSON": str(
                REPO / "src" / "models" / "tests" / "fixtures" / "glorys_pinned_catalog.json"
            ),
        },
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )
    if proc.returncode != 0:
        pytest.fail(
            "dry run Rscript failed:\n"
            + proc.stdout
            + "\n"
            + proc.stderr
        )
    manifest_path = out_dir / "cufes_pipeline_dry_run_manifest.json"
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["dry_run"] is True
    assert manifest["not_for_interpretation"] is True
    assert manifest["branch_existed"] is paths["branch_existed"]
    assert manifest["mode"] == paths["mode"]
    assert manifest.get("dropped_unavailable_covariates") == ["upwelling"]
    stage_names = [s["stage"] for s in manifest["stages"]]
    expected = [
        "load_model_data",
        "bottom_depth_qc",
        "barrier_mesh",
        "spatial_block_folds",
        "time_forward_scope",
        "fit_delta",
        "freeze_artifact",
        "spatial_cv_metrics",
        "predict_grid",
        "holdout_metrics",
    ]
    assert stage_names == expected
    assert all(s["ok"] for s in manifest["stages"])
    grid_csv = out_dir / f"{species}_prediction_grid_DRY_RUN.csv"
    assert grid_csv.is_file()
    header = grid_csv.read_text(encoding="utf-8").splitlines()[0]
    assert "DRY RUN" in header or "note" in header
    assert "data/provenance" not in str(out_dir)


def test_optional_bot2_worktree_build_sample(tmp_path: Path) -> None:
    """When bot2 branch is fetchable, build its synthetic table (read-only worktree)."""
    if os.environ.get("CI"):
        pytest.skip("read-only bot2 worktree build not run on CI workers")
    wt = tmp_path / "bot2_wt"
    fetch = subprocess.run(
        ["git", "fetch", "origin", "cursor/cufes-glorys-training-covariates-faff"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if fetch.returncode != 0:
        pytest.skip("could not fetch bot2 branch")
    add = subprocess.run(
        [
            "git",
            "worktree",
            "add",
            "--detach",
            str(wt),
            "origin/cursor/cufes-glorys-training-covariates-faff",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if add.returncode != 0:
        pytest.skip(add.stderr or add.stdout)
    try:
        script = """
import sys
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root / "src"))
sys.path.insert(0, str(root / "tests" / "ingestion" / "physics"))
import datetime as dt
import pandas as pd
from cufes_glorys_synthetic_fixture import glorys_store_from_synthetic_days
from fishai.ingestion.physics.cufes_training_covariates import (
    TRAINING_OUTPUT_COLUMNS,
    build_cufes_training_covariates_table,
)
events = pd.DataFrame(
    {
        "event_id": ["e1"],
        "start_time": pd.to_datetime(["2021-03-15T12:00:00Z"], utc=True),
        "stop_time": pd.to_datetime(["2021-03-15T12:12:00Z"], utc=True),
        "start_latitude": [33.0],
        "start_longitude": [-120.0],
        "stop_latitude": [33.01],
        "stop_longitude": [-119.99],
    }
)
store = glorys_store_from_synthetic_days([dt.date(2021, 3, 15)])
out, _qc, _drops, _floor = build_cufes_training_covariates_table(events, store)
assert set(out.columns) == set(TRAINING_OUTPUT_COLUMNS)
print("ok", out.shape[0])
"""
        proc = subprocess.run(
            ["python3", "-c", script, str(wt)],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0 and "pyproj" in (proc.stderr or ""):
            pytest.skip("bot2 worktree build requires pyproj in this environment")
        assert proc.returncode == 0, proc.stderr or proc.stdout
        assert "ok 1" in proc.stdout
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(wt)],
            cwd=REPO,
            capture_output=True,
            check=False,
        )
