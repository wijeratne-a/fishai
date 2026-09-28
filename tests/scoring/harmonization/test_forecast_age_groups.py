"""Forecast-age score grouping (not valid_offset_h)."""

from __future__ import annotations

import pandas as pd
import pytest

from fishai.scoring.harmonization.forecast_age import (
    NOWCAST_GROUP,
    assert_not_grouped_by_valid_offset_h,
    enrich_pairing_forecast_metadata,
    forecast_age_hours,
    forecast_group_label,
    grouping_keys_for_scores,
    is_nowcast_group,
    lead_days_from_forecast_age_hours,
)


def _row(age: float, fallback: bool = False, ocean_time: str = "2025-09-01T12:00:00Z") -> dict:
    return {
        "ocean_time": ocean_time,
        "source_run_time": "2025-09-01T03:00:00Z",
        "forecast_age_hours": age,
        "fallback_used": fallback,
        "obs_value": 15.0,
        "wcofs_coarsened_mapped": 15.1,
    }


def test_normal_run_nowcast_group() -> None:
    age = forecast_age_hours(0.0, 0)
    assert is_nowcast_group(age, False)
    df = enrich_pairing_forecast_metadata(pd.DataFrame([_row(age)]))
    assert df["forecast_group"].iloc[0] == NOWCAST_GROUP
    assert pd.isna(df["lead_days"].iloc[0])


def test_one_missed_run_lead_group() -> None:
    offset = 6.0
    age = forecast_age_hours(offset, 1)
    assert age == offset + 24
    assert not is_nowcast_group(age, False)
    label = forecast_group_label(age, False)
    assert label == f"lead_days_{lead_days_from_forecast_age_hours(age)}"
    df = enrich_pairing_forecast_metadata(pd.DataFrame([_row(age)]))
    assert df["forecast_group"].iloc[0] != NOWCAST_GROUP


def test_two_missed_runs_no_nowcast() -> None:
    offset = 6.0
    age = forecast_age_hours(offset, 2)
    assert age == offset + 48
    assert not is_nowcast_group(age, False)
    days = lead_days_from_forecast_age_hours(age)
    assert days in (2, 3)
    df = enrich_pairing_forecast_metadata(pd.DataFrame([_row(age)]))
    assert df["forecast_group"].iloc[0].startswith("lead_days_")
    assert df["forecast_group"].iloc[0] != NOWCAST_GROUP


def test_refuses_grouping_by_valid_offset_h() -> None:
    with pytest.raises(ValueError, match="valid_offset_h"):
        assert_not_grouped_by_valid_offset_h(("stratum", "valid_offset_h"))


def test_score_group_keys_exclude_valid_offset_h() -> None:
    assert "valid_offset_h" not in grouping_keys_for_scores()
