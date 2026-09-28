"""Recorded WCOFS avg.nowcast gaps (real-data preview; fit-window diagnostics)."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fishai.physics.store import CycleNotAvailable

REASON_CYCLE_NOT_AVAILABLE = "CycleNotAvailable"


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


def wcofs_avg_nowcast_unavailable_days(config: dict[str, Any]) -> frozenset[dt.date]:
    wcofs = config.get("wcofs") or {}
    spec = wcofs.get("avg_nowcast_unavailable") or {}
    return frozenset(_expand_date_ranges(spec))


def wcofs_avg_nowcast_missing_fit_days(config: dict[str, Any]) -> list[dt.date]:
    """Fit-split days with no avg.nowcast on NOAA PDS (recorded preview)."""
    fit_start = _config_date(config["split"]["fit_start"])
    fit_end = _config_date(config["split"]["fit_end"])
    missing = [
        day
        for day in sorted(wcofs_avg_nowcast_unavailable_days(config))
        if fit_start <= day <= fit_end
    ]
    return missing


def assert_wcofs_avg_nowcast_available(day: dt.date, config: dict[str, Any]) -> None:
    if day in wcofs_avg_nowcast_unavailable_days(config):
        raise CycleNotAvailable(
            f"WCOFS avg.nowcast not published for {day.isoformat()} (recorded preview gap)"
        )


def wcofs_avg_nowcast_missing_fit_day_records(config: dict[str, Any]) -> list[dict[str, str]]:
    wcofs = config.get("wcofs") or {}
    reason = str((wcofs.get("avg_nowcast_unavailable") or {}).get("reason_code", REASON_CYCLE_NOT_AVAILABLE))
    return [
        {"day": day.isoformat(), "reason_code": reason, "product": "avg.nowcast"}
        for day in wcofs_avg_nowcast_missing_fit_days(config)
    ]
