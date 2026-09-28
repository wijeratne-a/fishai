"""WCOFS UTC calendar-day hourly pairing schedule (PR #11 / auditbot1)."""

from __future__ import annotations

import datetime as dt

import numpy as np
import xarray as xr

from fishai.ingestion.physics.wcofs_utc_daily_pairing import (
    assert_avg_nowcast_ocean_time_covers_utc_day,
    assert_utc_valid_times_cover_calendar_day,
    utc_valid_times_for_calendar_day,
    valid_time_utc_for_cycle_lead,
    wcofs_fields_cycle_lead_for_utc_hour,
    wcofs_utc_daily_mean_fields,
)


def test_valid_times_cover_utc_day_exactly() -> None:
    day = dt.date(2024, 9, 15)
    times = utc_valid_times_for_calendar_day(day)
    assert_utc_valid_times_cover_calendar_day(day, times)
    assert times[0] == dt.datetime(2024, 9, 15, 0, 0)
    assert times[-1] == dt.datetime(2024, 9, 15, 23, 0)
    assert times[-1] < dt.datetime(2024, 9, 16, 0, 0)


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
        n = 3
        temp = np.full((1, n, 2, 2), float(len(seen)), dtype=float)
        return xr.Dataset(
            {
                "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp),
                "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp + 10),
            },
            coords={"ocean_time": [np.datetime64("2024-09-02T12:00:00")]},
        )

    out = wcofs_utc_daily_mean_fields(day, open_fields_lead=opener)
    assert len(seen) == 24
    assert out.attrs["wcofs_utc_daily_pairing"] == "hourly_utc_mean"
    assert float(out["temp"].mean()) == 12.5


def test_avg_nowcast_ocean_time_must_match_day() -> None:
    day = dt.date(2024, 9, 3)
    ds = xr.Dataset(coords={"ocean_time": [np.datetime64(f"{day.isoformat()}T12:00:00")]})
    assert_avg_nowcast_ocean_time_covers_utc_day(ds, day)
    bad = xr.Dataset(coords={"ocean_time": [np.datetime64("2024-09-04T12:00:00")]})
    try:
        assert_avg_nowcast_ocean_time_covers_utc_day(bad, day)
    except ValueError:
        return
    raise AssertionError("expected ValueError for mismatched ocean_time")
