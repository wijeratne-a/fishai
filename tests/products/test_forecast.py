"""72-hour egg-encounter forecast plan and public map."""

from __future__ import annotations

import pytest

from fishai.products.forecast import forecast_plan
from fishai.products.static_maps import render_static_map
from fishai.products.surface_contract import validate_prediction_rows


def test_plan_is_three_days() -> None:
    steps = forecast_plan("2024-06-02")
    assert [s["lead_days"] for s in steps] == [1, 2, 3]
    assert [s["forecast_age_hours"] for s in steps] == [24, 48, 72]
    assert [s["valid_day"] for s in steps] == ["2024-06-03", "2024-06-04", "2024-06-05"]
    assert all(s["evidence_state"] == "FORECAST" and s["life_stage"] == "egg" for s in steps)


def test_other_horizons_rejected() -> None:
    with pytest.raises(ValueError, match="72"):
        forecast_plan("2024-06-02", horizon_hours=48)


def test_forecast_rows_map_as_forecast() -> None:
    rows = []
    for lead, day, age in ((1, "2024-06-03", 24), (2, "2024-06-04", 48), (3, "2024-06-05", 72)):
        rows.append(
            {
                "cell_id": "g11_22",
                "species": "anchovy",
                "valid_day": day,
                "p_encounter": 0.15,
                "p_lo90": 0.05,
                "p_hi90": 0.4,
                "ood_level": 0,
                "evidence_state": "FORECAST",
                "unknown_reason": None,
                "lead_days": lead,
                "forecast_age_hours": age,
                "source_run_time": "2024-06-02T00:00:00Z",
                "fallback_used": False,
                "valid_time": f"{day}T00:00:00Z",
                "dry_run": False,
                "product_label": "egg encounter (eggs sampled near 3 m depth along ship tracks)",
                "reference_volume_m3": 11.0,
            }
        )
    rows.append(
        {
            **rows[0],
            "cell_id": "g11_23",
            "p_encounter": None,
            "p_lo90": None,
            "p_hi90": None,
            "ood_level": 3,
            "evidence_state": "UNKNOWN",
            "unknown_reason": "ood_level_ge_2",
        }
    )
    validate_prediction_rows(rows)
    html = render_static_map(rows)
    assert "Forecast" in html
    assert "Unknown" in html
    assert "spawning" in html.lower()
