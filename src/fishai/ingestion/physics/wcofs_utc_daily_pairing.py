"""
WCOFS fields nowcast scheduling for UTC calendar-day daily means (PR #11 rule).

Cycle ``R`` at 03Z: lead ``nNNN`` is valid at ``R 03Z + (NNN - 24)`` hours.
For UTC day ``D``, hours 00–03Z use cycle ``D`` leads ``n021``–``n024``; hours 04–23Z
use cycle ``D+1`` leads ``n001``–``n020``.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Sequence

import numpy as np
import xarray as xr

CYCLE_ISSUE_HOUR_UTC = 3


def wcofs_fields_cycle_lead_for_utc_hour(utc_day: dt.date, hour: int) -> tuple[dt.date, str]:
    if not 0 <= hour <= 23:
        raise ValueError(f"hour must be 0-23, got {hour}")
    if hour <= 3:
        return utc_day, f"n{21 + hour:03d}"
    return utc_day + dt.timedelta(days=1), f"n{hour - 3:03d}"


def valid_time_utc_for_cycle_lead(cycle_day: dt.date, lead: str) -> dt.datetime:
    n = int(lead[1:])
    offset_hours = n - 24
    cycle_start = dt.datetime.combine(cycle_day, dt.time(CYCLE_ISSUE_HOUR_UTC))
    return cycle_start + dt.timedelta(hours=offset_hours)


def utc_valid_times_for_calendar_day(utc_day: dt.date) -> list[dt.datetime]:
    """Twenty-four UTC instants from ``utc_day`` 00:00 through 23:00 inclusive."""
    return [
        valid_time_utc_for_cycle_lead(*wcofs_fields_cycle_lead_for_utc_hour(utc_day, hour))
        for hour in range(24)
    ]


def assert_utc_valid_times_cover_calendar_day(utc_day: dt.date, times: Sequence[dt.datetime]) -> None:
    """Hard-fail unless ``times`` are exactly ``D`` 00Z … 23Z with no spill into ``D+1`` 00Z."""
    expected = utc_valid_times_for_calendar_day(utc_day)
    if len(times) != 24:
        raise ValueError(f"expected 24 valid times, got {len(times)}")
    for got, want in zip(times, expected, strict=True):
        if got != want:
            raise ValueError(f"valid time mismatch: got {got!r}, want {want!r}")
    day_end = dt.datetime.combine(utc_day + dt.timedelta(days=1), dt.time(0))
    if any(t >= day_end for t in times):
        raise ValueError("valid time at or after next-day 00Z")
    if times[0] != dt.datetime.combine(utc_day, dt.time(0)):
        raise ValueError("first valid time must be calendar-day 00Z")


def _ocean_time_to_utc_datetime(value: object) -> dt.datetime:
    if isinstance(value, dt.datetime):
        return value.replace(tzinfo=None)
    if isinstance(value, np.datetime64):
        ts = (value - np.datetime64("1970-01-01T00:00:00")) / np.timedelta64(1, "s")
        return dt.datetime.utcfromtimestamp(float(ts))
    raise TypeError(f"unsupported ocean_time value: {value!r}")


def assert_avg_nowcast_ocean_time_covers_utc_day(ds: xr.Dataset, utc_day: dt.date) -> None:
    """
    avg.nowcast files must document a daily mean whose ``ocean_time`` lies on ``utc_day``.

    Full 24-hour composition is validated via ``hourly_utc_mean`` pairing; this guard
    ensures avg.nowcast metadata is not silently misaligned.
    """
    if "ocean_time" not in ds.variables and "ocean_time" not in ds.dims:
        raise ValueError("avg.nowcast dataset missing ocean_time")
    ot = ds["ocean_time"]
    if ot.size < 1:
        raise ValueError("avg.nowcast ocean_time is empty")
    when = _ocean_time_to_utc_datetime(ot.values.flat[0])
    if when.date() != utc_day:
        raise ValueError(
            f"avg.nowcast ocean_time date {when.date()} does not match pairing day {utc_day}"
        )


OpenFieldsLead = Callable[[dt.date, str], xr.Dataset]


def wcofs_utc_daily_mean_fields(
    utc_day: dt.date,
    *,
    open_fields_lead: OpenFieldsLead,
) -> xr.Dataset:
    """Area-naive elementwise mean of 24 hourly WCOFS fields slabs for UTC day ``utc_day``."""
    slabs: list[xr.Dataset] = []
    valid_times: list[dt.datetime] = []
    for hour in range(24):
        cycle, lead = wcofs_fields_cycle_lead_for_utc_hour(utc_day, hour)
        valid_times.append(valid_time_utc_for_cycle_lead(cycle, lead))
        slabs.append(open_fields_lead(cycle, lead))
    assert_utc_valid_times_cover_calendar_day(utc_day, valid_times)

    ref = slabs[0]
    temp_acc = None
    salt_acc = None
    count = 0
    for slab in slabs:
        s = slab.isel(ocean_time=0) if "ocean_time" in slab.dims else slab
        t = s["temp"].values
        sa = s["salt"].values
        if temp_acc is None:
            temp_acc = np.zeros_like(t, dtype=float)
            salt_acc = np.zeros_like(sa, dtype=float)
        temp_acc += t
        salt_acc += sa
        count += 1
    temp_acc /= count
    salt_acc /= count
    out = ref.isel(ocean_time=0).copy(deep=True) if "ocean_time" in ref.dims else ref.copy(deep=True)
    out["temp"].values = temp_acc
    out["salt"].values = salt_acc
    out.attrs["wcofs_utc_daily_pairing"] = "hourly_utc_mean"
    out.attrs["wcofs_utc_day"] = utc_day.isoformat()
    return out
