"""WCOFS UTC calendar-day hourly pairing schedule (PR #11 / auditbot1)."""

from __future__ import annotations

import datetime as dt
import json

import numpy as np
import pytest
import xarray as xr

from fishai.ingestion.physics.wcofs_utc_daily_pairing import (
    REASON_DUPLICATE_HOUR,
    REASON_MISSING_HOUR,
    REASON_OCEAN_TIME_MISMATCH,
    REASON_OPEN_FAILED,
    WcofsUtcDailyMeanIncompleteError,
    assert_avg_nowcast_ocean_time_covers_utc_day,
    assert_utc_valid_times_cover_calendar_day,
    hourly_fields_slots_for_utc_day,
    utc_valid_times_for_calendar_day,
    valid_time_utc_for_cycle_lead,
    wcofs_fields_cycle_lead_for_utc_hour,
    wcofs_utc_daily_mean_fields,
)


def _fields_slab(when: dt.datetime, tag: float) -> xr.Dataset:
    n = 3
    temp = np.full((1, n, 2, 2), tag, dtype=float)
    return xr.Dataset(
        {
            "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp),
            "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp + 10),
        },
        coords={"ocean_time": [np.datetime64(when.strftime("%Y-%m-%dT%H:%M:%S"))]},
        attrs={"wcofs_s3_key": f"mock/{when.isoformat()}"},
    )


def test_valid_times_cover_utc_day_exactly() -> None:
    day = dt.date(2024, 9, 15)
    times = utc_valid_times_for_calendar_day(day)
    assert_utc_valid_times_cover_calendar_day(day, times)
    assert times[0] == dt.datetime(2024, 9, 15, 0, 0)
    assert times[-1] == dt.datetime(2024, 9, 15, 23, 0)
    assert times[-1] < dt.datetime(2024, 9, 16, 0, 0)


def test_full_hourly_mapping_run_d_and_run_d_plus_one() -> None:
    day = dt.date(2024, 9, 10)
    slots = hourly_fields_slots_for_utc_day(day)
    assert len(slots) == 24
    for hour in range(4):
        assert slots[hour].cycle == day
        assert slots[hour].lead == f"n{21 + hour:03d}"
    for hour in range(4, 24):
        assert slots[hour].cycle == day + dt.timedelta(days=1)
        assert slots[hour].lead == f"n{hour - 3:03d}"
    assert slots[0].expected_valid_time_utc == dt.datetime(2024, 9, 10, 0, 0)
    assert slots[3].expected_valid_time_utc == dt.datetime(2024, 9, 10, 3, 0)
    assert slots[4].expected_valid_time_utc == dt.datetime(2024, 9, 10, 4, 0)
    assert slots[23].expected_valid_time_utc == dt.datetime(2024, 9, 10, 23, 0)


def test_midnight_hours_use_same_day_cycle() -> None:
    cycle, lead = wcofs_fields_cycle_lead_for_utc_hour(dt.date(2024, 9, 1), 0)
    assert cycle == dt.date(2024, 9, 1)
    assert lead == "n021"
    when = valid_time_utc_for_cycle_lead(cycle, lead)
    assert when == dt.datetime(2024, 9, 1, 0, 0)


def test_hourly_mean_opener_invoked_for_all_leads() -> None:
    day = dt.date(2024, 9, 2)
    seen: list[tuple[dt.date, str]] = []

    def opener(cycle: dt.date, lead: str) -> xr.Dataset:
        seen.append((cycle, lead))
        when = valid_time_utc_for_cycle_lead(cycle, lead)
        return _fields_slab(when, float(len(seen)))

    out = wcofs_utc_daily_mean_fields(day, open_fields_lead=opener)
    assert len(seen) == 24
    assert out.attrs["wcofs_utc_daily_pairing"] == "hourly_utc_mean"
    assert float(out["temp"].mean()) == 12.5
    prov = json.loads(out.attrs["wcofs_utc_daily_provenance"])
    assert prov["utc_day"] == day.isoformat()
    assert len(prov["sources"]) == 24
    assert prov["sources"][0]["lead"] == "n021"
    assert prov["sources"][0]["cycle"] == day.isoformat()
    assert prov["sources"][4]["lead"] == "n001"
    assert prov["sources"][4]["cycle"] == (day + dt.timedelta(days=1)).isoformat()


def test_duplicate_ocean_time_rejects_whole_day() -> None:
    day = dt.date(2024, 9, 5)

    def opener(cycle: dt.date, lead: str) -> xr.Dataset:
        when = valid_time_utc_for_cycle_lead(cycle, lead)
        if lead == "n023":
            when = valid_time_utc_for_cycle_lead(cycle, "n022")
        return _fields_slab(when, 1.0)

    with pytest.raises(WcofsUtcDailyMeanIncompleteError) as excinfo:
        wcofs_utc_daily_mean_fields(day, open_fields_lead=opener)
    assert excinfo.value.reason_code == REASON_DUPLICATE_HOUR


def test_missing_hour_rejects_whole_day() -> None:
    day = dt.date(2024, 9, 6)

    def opener(cycle: dt.date, lead: str) -> xr.Dataset:
        when = valid_time_utc_for_cycle_lead(cycle, lead)
        if lead == "n015":
            raise FileNotFoundError("simulated missing object")
        return _fields_slab(when, 1.0)

    with pytest.raises(WcofsUtcDailyMeanIncompleteError) as excinfo:
        wcofs_utc_daily_mean_fields(day, open_fields_lead=opener)
    assert excinfo.value.reason_code == REASON_OPEN_FAILED


def test_ocean_time_mismatch_rejects_whole_day() -> None:
    day = dt.date(2024, 9, 7)

    def opener(cycle: dt.date, lead: str) -> xr.Dataset:
        when = valid_time_utc_for_cycle_lead(cycle, lead)
        if lead == "n010":
            when = dt.datetime(2024, 9, 7, 12, 30)
        return _fields_slab(when, 1.0)

    with pytest.raises(WcofsUtcDailyMeanIncompleteError) as excinfo:
        wcofs_utc_daily_mean_fields(day, open_fields_lead=opener)
    assert excinfo.value.reason_code == REASON_OCEAN_TIME_MISMATCH


def test_avg_nowcast_ocean_time_must_match_day() -> None:
    day = dt.date(2024, 9, 3)
    ds = xr.Dataset(coords={"ocean_time": [np.datetime64(f"{day.isoformat()}T12:00:00")]})
    assert_avg_nowcast_ocean_time_covers_utc_day(ds, day)
    bad = xr.Dataset(coords={"ocean_time": [np.datetime64("2024-09-04T12:00:00")]})
    with pytest.raises(ValueError):
        assert_avg_nowcast_ocean_time_covers_utc_day(bad, day)
