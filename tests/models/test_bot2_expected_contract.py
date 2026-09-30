"""Expected bot2 contract helpers (schema mode + synthetic fixtures)."""

from __future__ import annotations

from pathlib import Path

from fishai.models.bot2_expected_contract import (
    SYNTHETIC_FIXTURE_NOTE,
    expected_training_output_columns,
    harness_run_metadata,
    resolve_bot2_schema_mode,
)

_TEST_DIR = Path(__file__).resolve().parent
import sys

if str(_TEST_DIR) not in sys.path:
    sys.path.insert(0, str(_TEST_DIR))
from bot2_spring_subset_fixtures import write_minimal_expected_contract_csvs


def test_synthetic_fixture_note_is_marked() -> None:
    assert "SYNTHETIC" in SYNTHETIC_FIXTURE_NOTE


def test_minimal_expected_contract_csv(tmp_path: Path) -> None:
    paths = write_minimal_expected_contract_csvs(tmp_path)
    text = paths["covariates"].read_text(encoding="utf-8")
    assert "SYNTHETIC_expected_bot2_contract" in text
    assert "no_consistent_wind_product" in text
    assert paths["mode"] == "expected"


def test_resolve_mode_explicit() -> None:
    assert resolve_bot2_schema_mode("expected") == "expected"
    assert resolve_bot2_schema_mode("git") == "git"


def test_expected_columns_include_physics_and_metadata() -> None:
    cols = expected_training_output_columns()
    assert "T3m" in cols
    assert "upwelling_status" in cols
    meta = harness_run_metadata(mode="expected")
    assert meta["mode"] == "expected"
