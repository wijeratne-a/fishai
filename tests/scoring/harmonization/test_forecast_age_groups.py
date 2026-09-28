"""Forecast-age score grouping (not valid_offset_h)."""

from __future__ import annotations

import pandas as pd
import pytest

from fishai.scoring.harmonization.forecast_age import (
    NOWCAST_GROUP,
    assert_not_grouped_by_valid_offset_h,
    enrich_pairing_forecast_metadata,
    forecast_group_label,
    grouping_keys_for_scores,
    is_nowcast_group,
    lead_days_from_forecast_age_hours,
)
from fishai.scoring.harmonization.wcofs_ocean_time import forecast_age_hours_from_ocean_time

RUN = "2025-09-01T03:00:00Z"


def _row_from_age_hours(age_h: float, fallback: bool = False) -> dict:
    run_ts = pd.Timestamp(RUN)
    ocean_ts = run_ts + pd.Timedelta(hours=age_h)
    ocean = ocean_ts.strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "ocean_time": ocean,
        "source_run_time": RUN,
        "forecast_age_hours": age_h,
        "fallback_used": fallback,
        "obs_value": 15.0,
        "wcofs_coarsened_mapped": 15.1,
        "date": "2025-09-01",
        "variable": "sea_water_temperature",
        "nearshore": True,
        "obs_id": "b0",
        "wcofs_native": 15.0,
        "wcofs_coarsened": 15.0,
        "glorys": 15.0,
    }


def test_normal_run_nowcast_group() -> None:
    age = forecast_age_hours_from_ocean_time(_row_from_age_hours(0.0)["ocean_time"], RUN)
    assert age == 0.0
    assert is_nowcast_group(age, False)
    df = enrich_pairing_forecast_metadata(pd.DataFrame([_row_from_age_hours(0.0)]))
    assert df["forecast_group"].iloc[0] == NOWCAST_GROUP
    assert pd.isna(df["lead_days"].iloc[0])


def test_one_missed_run_lead_group() -> None:
    age = forecast_age_hours_from_ocean_time(
        _row_from_age_hours(30.0)["ocean_time"],
        RUN,
    )
    assert age == 30.0
    assert not is_nowcast_group(age, False)
    label = forecast_group_label(age, False)
    assert label == f"lead_days_{lead_days_from_forecast_age_hours(age)}"
    df = enrich_pairing_forecast_metadata(pd.DataFrame([_row_from_age_hours(30.0)]))
    assert df["forecast_group"].iloc[0] != NOWCAST_GROUP


def test_two_missed_runs_no_nowcast() -> None:
    age = forecast_age_hours_from_ocean_time(
        _row_from_age_hours(54.0)["ocean_time"],
        RUN,
    )
    assert age == 54.0
    assert not is_nowcast_group(age, False)
    days = lead_days_from_forecast_age_hours(age)
    assert days in (2, 3)
    df = enrich_pairing_forecast_metadata(pd.DataFrame([_row_from_age_hours(54.0)]))
    assert df["forecast_group"].iloc[0].startswith("lead_days_")
    assert df["forecast_group"].iloc[0] != NOWCAST_GROUP


def test_refuses_grouping_by_valid_offset_h() -> None:
    with pytest.raises(ValueError, match="valid_offset_h"):
        assert_not_grouped_by_valid_offset_h(("stratum", "valid_offset_h"))


def test_score_group_keys_exclude_valid_offset_h() -> None:
    assert "valid_offset_h" not in grouping_keys_for_scores()
