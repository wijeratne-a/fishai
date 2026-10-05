"""Nowcast day selection and plan."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fishai.products.nowcast import latest_glorys_valid_day, nowcast_plan
from fishai.products.static_maps import render_static_map
from fishai.products.surface_contract import validate_prediction_rows

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "glorys_days.json"


def test_latest_day_and_plan() -> None:
    day = latest_glorys_valid_day(FIXTURE)
    assert day == "2024-06-02"
    plan = nowcast_plan(day)
    assert plan["mode"] == "nowcast"
    assert plan["lead_days"] == 0
    assert plan["forecast_age_hours"] == 0
    assert plan["evidence_state"] == "NOWCAST_UNVALIDATED"
    assert plan["life_stage"] == "egg"


def test_empty_index_fails(tmp_path: Path) -> None:
    path = tmp_path / "days.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        latest_glorys_valid_day(path)


def test_nowcast_row_publishes_as_current_nowcast() -> None:
    row = {
        "cell_id": "g10_20",
        "species": "sardine",
        "valid_day": "2024-06-02",
        "p_encounter": 0.22,
        "p_lo90": 0.1,
        "p_hi90": 0.4,
        "ood_level": 0,
        "evidence_state": "NOWCAST_UNVALIDATED",
        "unknown_reason": None,
        "lead_days": 0,
        "forecast_age_hours": 0,
        "source_run_time": "2024-06-02T00:00:00Z",
        "fallback_used": False,
        "valid_time": "2024-06-02T00:00:00Z",
        "dry_run": False,
        "product_label": "egg encounter (eggs sampled near 3 m depth along ship tracks)",
        "reference_volume_m3": 12.4,
    }
    validate_prediction_rows([row])
    html = render_static_map([row])
    assert "Current Nowcast" in html
    assert "spawning" in html.lower()


def test_fixture_file_is_json_list() -> None:
    days = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert days == ["2024-06-01", "2024-06-02"]
