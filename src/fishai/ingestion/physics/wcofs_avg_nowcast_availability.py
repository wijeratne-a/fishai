"""Recorded WCOFS nowcast gaps (real-data preview; overlap pairing exclusions)."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fishai.ingestion.physics.wcofs_glorys_grid import EVIDENCE_STATE_UNKNOWN

REASON_WCOFS_NOWCAST_MISSING = "wcofs_nowcast_missing"


class WcofsNowcastMissingDayError(Exception):
    """WCOFS nowcast is unavailable for this UTC day (no fill, no forecast substitution)."""

    def __init__(self, day: dt.date, message: str | None = None) -> None:
        super().__init__(message or f"WCOFS nowcast missing for {day.isoformat()}")
        self.day = day
        self.reason_code = REASON_WCOFS_NOWCAST_MISSING
        self.evidence_state = EVIDENCE_STATE_UNKNOWN


def _config_date(value: Any) -> dt.date:
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def _expand_date_ranges(spec: dict[str, Any]) -> list[dt.date]:
    days: list[dt.date] = []
    for raw in spec.get("dates") or []:
        days.append(_config_date(raw))
    for block in spec.get("ranges") or []:
        start = _config_date(block["start"])
        end = _config_date(block["end"])
        cur = start
        while cur <= end:
            days.append(cur)
            cur += dt.timedelta(days=1)
    return sorted(set(days))


def wcofs_nowcast_missing_days(config: dict[str, Any]) -> frozenset[dt.date]:
    wcofs = config.get("wcofs") or {}
    spec = wcofs.get("avg_nowcast_unavailable") or {}
    return frozenset(_expand_date_ranges(spec))


def wcofs_nowcast_missing_fit_days(config: dict[str, Any]) -> list[dt.date]:
    """Fit-split days with no WCOFS nowcast on NOAA PDS (recorded preview)."""
    fit_start = _config_date(config["split"]["fit_start"])
    fit_end = _config_date(config["split"]["fit_end"])
    return [
        day
        for day in sorted(wcofs_nowcast_missing_days(config))
        if fit_start <= day <= fit_end
    ]


def is_wcofs_nowcast_missing_day(day: dt.date, config: dict[str, Any]) -> bool:
    return day in wcofs_nowcast_missing_days(config)


def assert_wcofs_nowcast_available(day: dt.date, config: dict[str, Any]) -> None:
    if is_wcofs_nowcast_missing_day(day, config):
        raise WcofsNowcastMissingDayError(day)


# Back-compat aliases (avg.nowcast product name in recorded preview).
wcofs_avg_nowcast_unavailable_days = wcofs_nowcast_missing_days
wcofs_avg_nowcast_missing_fit_days = wcofs_nowcast_missing_fit_days
assert_wcofs_avg_nowcast_available = assert_wcofs_nowcast_available


def wcofs_nowcast_missing_day_records(
    config: dict[str, Any],
    *,
    days: list[dt.date] | None = None,
) -> list[dict[str, str]]:
    target_days = days if days is not None else wcofs_nowcast_missing_fit_days(config)
    return [
        {
            "day": day.isoformat(),
            "reason_code": REASON_WCOFS_NOWCAST_MISSING,
            "evidence_state": EVIDENCE_STATE_UNKNOWN,
            "product": "avg.nowcast",
        }
        for day in target_days
    ]


def wcofs_avg_nowcast_missing_fit_day_records(config: dict[str, Any]) -> list[dict[str, str]]:
    return wcofs_nowcast_missing_day_records(config)
