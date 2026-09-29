"""
WCOFS fields nowcast scheduling for UTC calendar-day daily means (PR #11 rule).

Cycle ``R`` at 03Z: lead ``nNNN`` is valid at ``R 03Z + (NNN - 24)`` hours.
For UTC day ``D``, hours 00–03Z use cycle ``D`` leads ``n021``–``n024``; hours 04–23Z
use cycle ``D+1`` leads ``n001``–``n020``.
"""

from __future__ import annotations

import datetime as dt
import json
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from typing import Any, Literal

import numpy as np
import xarray as xr

CYCLE_ISSUE_HOUR_UTC = 3

ReasonCode = Literal[
    "missing_hour",
    "duplicate_hour",
    "ocean_time_mismatch",
    "open_failed",
]

REASON_MISSING_HOUR = "missing_hour"
REASON_DUPLICATE_HOUR = "duplicate_hour"
REASON_OCEAN_TIME_MISMATCH = "ocean_time_mismatch"
REASON_OPEN_FAILED = "open_failed"


@dataclass(frozen=True)
class HourlyFieldsSlot:
    """One hourly slab in the UTC daily mean."""

    hour: int
    cycle: dt.date
    lead: str
    expected_valid_time_utc: dt.datetime


@dataclass(frozen=True)
class FieldsLeadProvenance:
    cycle: str
    lead: str
    expected_valid_time_utc: str
    ocean_time_utc: str | None
    s3_key: str | None


@dataclass(frozen=True)
class WcofsUtcDailyMeanProvenance:
    utc_day: str
    pairing: str
    sources: tuple[FieldsLeadProvenance, ...]


class WcofsUtcDailyMeanIncompleteError(Exception):
    """Raised when fewer than 24 distinct valid UTC hours are available for one calendar day."""

    def __init__(
        self,
        utc_day: dt.date,
        reason_code: ReasonCode,
        message: str,
        *,
        provenance: WcofsUtcDailyMeanProvenance | None = None,
    ) -> None:
        super().__init__(message)
        self.utc_day = utc_day
        self.reason_code = reason_code
        self.provenance = provenance


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


def hourly_fields_slots_for_utc_day(utc_day: dt.date) -> list[HourlyFieldsSlot]:
    slots: list[HourlyFieldsSlot] = []
    for hour in range(24):
        cycle, lead = wcofs_fields_cycle_lead_for_utc_hour(utc_day, hour)
        expected = valid_time_utc_for_cycle_lead(cycle, lead)
        slots.append(
            HourlyFieldsSlot(
                hour=hour,
                cycle=cycle,
                lead=lead,
                expected_valid_time_utc=expected,
            )
        )
    return slots


def utc_valid_times_for_calendar_day(utc_day: dt.date) -> list[dt.datetime]:
    """Twenty-four UTC instants from ``utc_day`` 00:00 through 23:00 inclusive."""
    return [slot.expected_valid_time_utc for slot in hourly_fields_slots_for_utc_day(utc_day)]


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


def ocean_time_utc_from_fields_slab(slab: xr.Dataset) -> dt.datetime:
    if "ocean_time" not in slab.variables and "ocean_time" not in slab.dims:
        raise ValueError("fields slab missing ocean_time")
    ot = slab["ocean_time"]
    if ot.size < 1:
        raise ValueError("fields slab ocean_time is empty")
    return _ocean_time_to_utc_datetime(ot.values.flat[0])


def validate_distinct_ocean_hours_for_utc_day(
    utc_day: dt.date,
    slabs: Sequence[tuple[HourlyFieldsSlot, xr.Dataset | None]],
) -> WcofsUtcDailyMeanProvenance:
    """
    Require exactly 24 slabs whose ``ocean_time`` matches each slot's expected UTC hour.

    Raises ``WcofsUtcDailyMeanIncompleteError`` on missing, duplicate, or mismatched hours.
    """
    sources: list[FieldsLeadProvenance] = []
    seen_hours: dict[dt.datetime, HourlyFieldsSlot] = {}

    for slot, slab in slabs:
        s3_key = None
        ocean_when: dt.datetime | None = None
        if slab is None:
            prov = FieldsLeadProvenance(
                cycle=slot.cycle.isoformat(),
                lead=slot.lead,
                expected_valid_time_utc=slot.expected_valid_time_utc.isoformat(sep="T"),
                ocean_time_utc=None,
                s3_key=None,
            )
            sources.append(prov)
            raise WcofsUtcDailyMeanIncompleteError(
                utc_day,
                REASON_MISSING_HOUR,
                f"missing fields slab for hour {slot.hour:02d} ({slot.cycle} {slot.lead})",
                provenance=WcofsUtcDailyMeanProvenance(
                    utc_day=utc_day.isoformat(),
                    pairing="hourly_utc_mean",
                    sources=tuple(sources),
                ),
            )
        s3_key = str(slab.attrs.get("wcofs_s3_key")) if slab.attrs.get("wcofs_s3_key") else None
        try:
            ocean_when = ocean_time_utc_from_fields_slab(slab)
        except ValueError as exc:
            sources.append(
                FieldsLeadProvenance(
                    cycle=slot.cycle.isoformat(),
                    lead=slot.lead,
                    expected_valid_time_utc=slot.expected_valid_time_utc.isoformat(sep="T"),
                    ocean_time_utc=None,
                    s3_key=s3_key,
                )
            )
            raise WcofsUtcDailyMeanIncompleteError(
                utc_day,
                REASON_MISSING_HOUR,
                str(exc),
                provenance=WcofsUtcDailyMeanProvenance(
                    utc_day=utc_day.isoformat(),
                    pairing="hourly_utc_mean",
                    sources=tuple(sources),
                ),
            ) from exc

        prov = FieldsLeadProvenance(
            cycle=slot.cycle.isoformat(),
            lead=slot.lead,
            expected_valid_time_utc=slot.expected_valid_time_utc.isoformat(sep="T"),
            ocean_time_utc=ocean_when.isoformat(sep="T"),
            s3_key=s3_key,
        )
        sources.append(prov)

        if ocean_when in seen_hours:
            raise WcofsUtcDailyMeanIncompleteError(
                utc_day,
                REASON_DUPLICATE_HOUR,
                f"duplicate valid hour {ocean_when!r} from {slot.cycle} {slot.lead}",
                provenance=WcofsUtcDailyMeanProvenance(
                    utc_day=utc_day.isoformat(),
                    pairing="hourly_utc_mean",
                    sources=tuple(sources),
                ),
            )

        if ocean_when != slot.expected_valid_time_utc:
            raise WcofsUtcDailyMeanIncompleteError(
                utc_day,
                REASON_OCEAN_TIME_MISMATCH,
                (
                    f"ocean_time {ocean_when!r} != expected {slot.expected_valid_time_utc!r} "
                    f"for {slot.cycle} {slot.lead}"
                ),
                provenance=WcofsUtcDailyMeanProvenance(
                    utc_day=utc_day.isoformat(),
                    pairing="hourly_utc_mean",
                    sources=tuple(sources),
                ),
            )
        seen_hours[ocean_when] = slot

    if len(seen_hours) != 24:
        raise WcofsUtcDailyMeanIncompleteError(
            utc_day,
            REASON_MISSING_HOUR,
            f"expected 24 distinct hours, got {len(seen_hours)}",
            provenance=WcofsUtcDailyMeanProvenance(
                utc_day=utc_day.isoformat(),
                pairing="hourly_utc_mean",
                sources=tuple(sources),
            ),
        )

    return WcofsUtcDailyMeanProvenance(
        utc_day=utc_day.isoformat(),
        pairing="hourly_utc_mean",
        sources=tuple(sources),
    )


def provenance_to_json(provenance: WcofsUtcDailyMeanProvenance) -> str:
    return json.dumps(asdict(provenance), sort_keys=True)


def intended_glorys_day_valid_time_utc(utc_day: dt.date) -> dt.datetime:
    """Documented avg.nowcast ``ocean_time`` for cycle ``utc_day + 1 day`` (15:00 UTC on ``utc_day``)."""
    return dt.datetime.combine(utc_day, dt.time(15, 0), tzinfo=dt.timezone.utc)


def assert_avg_nowcast_ocean_time_covers_utc_day(ds: xr.Dataset, utc_day: dt.date) -> None:
    """
    avg.nowcast from cycle ``utc_day + 1`` must carry ``ocean_time`` at 15:00 UTC on ``utc_day``.

    Full 24-hour composition is validated via ``hourly_utc_mean`` pairing; this guard
    ensures avg.nowcast metadata is not silently misaligned.
    """
    if "ocean_time" not in ds.variables and "ocean_time" not in ds.dims:
        raise ValueError("avg.nowcast dataset missing ocean_time")
    ot = ds["ocean_time"]
    if ot.size < 1:
        raise ValueError("avg.nowcast ocean_time is empty")
    when = _ocean_time_to_utc_datetime(ot.values.flat[0])
    want = intended_glorys_day_valid_time_utc(utc_day).replace(tzinfo=None)
    if when != want:
        raise ValueError(
            f"avg.nowcast ocean_time {when!r} != intended {want!r} for glorys day {utc_day}"
        )


OpenFieldsLead = Callable[[dt.date, str], xr.Dataset]
