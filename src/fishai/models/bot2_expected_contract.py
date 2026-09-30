"""Expected bot2 training covariate contract (parameterized dry-run / schema mode)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from fishai.models.bot2_covariate_schema import (
    BOT2_BRANCH,
    BOT2_BRANCH_REF,
    local_cufes_covariate_fields,
)

REPO_ROOT = Path(__file__).resolve().parents[3]

# PR #4 CUFES event columns used by load_model_data (midpoint mesh uses lat/lon endpoints).
CUFES_EVENT_CONTRACT_COLUMNS = (
    "event_id",
    "time",
    "lat",
    "lon",
    "stop_lat",
    "stop_lon",
)

EXPECTED_BOT2_METADATA_COLUMNS = (
    "upwelling_status",
    "bottom_depth_m",
    "depth_at_model_floor",
    "source",
    "provenance",
    "excluded",
    "source_product",
    "excluded_reason",
)

PLANNED_COVARIATE_GAPS = {
    "upwelling": "no_consistent_wind_product",
}

SYNTHETIC_FIXTURE_NOTE = (
    "SYNTHETIC — expected bot2 contract table for dry-run harness only; not production data."
)


def expected_training_output_columns() -> tuple[str, ...]:
    fields = local_cufes_covariate_fields()
    return ("event_id", *fields, *EXPECTED_BOT2_METADATA_COLUMNS)


def bot2_branch_exists_on_remote(*, ref: str = BOT2_BRANCH) -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", ref],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def resolve_bot2_schema_mode(mode: str | None = None) -> str:
    """Return ``expected`` or ``git`` (never ``auto``)."""
    raw = (mode or os.environ.get("BOT2_SCHEMA_MODE", "auto")).strip().lower()
    if raw in ("expected", "git"):
        return raw
    if raw == "auto":
        return "git" if bot2_branch_exists_on_remote() else "expected"
    raise ValueError(f"unknown BOT2_SCHEMA_MODE {raw!r}; use auto, expected, or git")


def training_output_columns_for_mode(
    *,
    mode: str | None = None,
    git_ref: str = BOT2_BRANCH,
) -> tuple[str, ...]:
    from fishai.models.bot2_covariate_schema import bot2_training_output_columns

    resolved = resolve_bot2_schema_mode(mode)
    if resolved == "git":
        return bot2_training_output_columns(ref=git_ref)
    return expected_training_output_columns()


def harness_run_metadata(*, mode: str | None = None) -> dict[str, object]:
    resolved = resolve_bot2_schema_mode(mode)
    return {
        "bot2_branch_ref": BOT2_BRANCH_REF,
        "branch_existed": bot2_branch_exists_on_remote(),
        "mode": resolved,
        "synthetic_fixture_note": SYNTHETIC_FIXTURE_NOTE,
    }
