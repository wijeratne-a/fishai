"""Schema gate for egg-encounter prediction surfaces."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fishai.products.surface_contract import validate_prediction_rows

REPO = Path(__file__).resolve().parents[2]
FIXTURE = REPO / "tests" / "products" / "fixtures" / "hindcast_surface_rows.json"


def _row(**overrides):
    base = {
        "cell_id": "g10_20",
        "species": "sardine",
        "valid_day": "2016-07-01",
        "p_encounter": 0.2,
        "p_lo90": 0.1,
        "p_hi90": 0.3,
        "ood_level": 0,
        "evidence_state": "HINDCAST_GLORYS",
        "unknown_reason": None,
        "lead_days": 0,
        "forecast_age_hours": None,
        "source_run_time": None,
        "fallback_used": False,
        "valid_time": "2016-07-01T00:00:00Z",
        "dry_run": True,
        "product_label": "egg encounter (eggs sampled near 3 m depth along ship tracks)",
        "reference_volume_m3": 1.5,
    }
    base.update(overrides)
    return base


def test_fixture_and_both_species_validate() -> None:
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    validate_prediction_rows(rows)
    assert {r["species"] for r in rows} == {"sardine", "anchovy"}
    assert all(r["evidence_state"] == "HINDCAST_GLORYS" or r["p_encounter"] is None for r in rows)


def test_unknown_with_probability_fails() -> None:
    with pytest.raises(ValueError, match="null p_encounter"):
        validate_prediction_rows(
            [_row(evidence_state="UNKNOWN", unknown_reason="ood_level_ge_2", p_encounter=0.4, ood_level=2)]
        )


def test_ood_without_unknown_fails() -> None:
    with pytest.raises(ValueError, match="ood_level"):
        validate_prediction_rows([_row(ood_level=2)])
