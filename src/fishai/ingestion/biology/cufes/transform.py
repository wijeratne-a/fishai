"""QC, event construction, and occurrence wide-to-long for CUFES."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from fishai.ingestion.biology.cufes.constants import (
    DEFAULT_MAX_DURATION_MIN,
    DEFAULT_MIN_DURATION_MIN,
    EGG_CATEGORIES,
    LIFE_STAGE_EGG,
    PUMP_SPEED_MAX_M3_PER_MIN,
    PUMP_SPEED_MAX_START_STOP_RATIO,
    PUMP_SPEED_MIN_M3_PER_MIN,
    QC_COORD_INVALID,
    QC_COUNT_INVALID,
    QC_DURATION_OUT_OF_RANGE,
    QC_KEY_INVALID,
    QC_MISSING_STOP_TIME,
    QC_PUMP_INVALID,
    QC_REVERSED_TIME,
    QC_RULE_LABELS,
    ZERO_SEMANTICS,
)

__all__ = [
    "TransformResult",
    "make_event_id",
    "parse_egg_count",
    "parse_row_egg_counts",
    "qc_flags_for_row",
    "transform_rows",
    "volume_m3_for_row",
]


def make_event_id(cruise: str, ship_code: str, sample_number: str | int) -> str:
    return f"CUFES:{cruise}:{ship_code}:{sample_number}"


def _parse_erddap_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        epoch = float(text)
        return datetime.fromtimestamp(epoch, tz=timezone.utc)
    except ValueError:
        return None


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "na", ""}:
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    if math.isnan(out):
        return None
    return out


def _valid_lat_lon(lat: float | None, lon: float | None) -> bool:
    if lat is None or lon is None:
        return False
    if not (-90.0 <= lat <= 90.0):
        return False
    if not (-180.0 <= lon <= 180.0):
        return False
    return True


def _row_keys(row: Mapping[str, Any]) -> tuple[str, str, str]:
    cruise = str(row.get("cruise", "")).strip()
    ship_code = str(row.get("ship_code", "")).strip()
    sample_number = str(row.get("sample_number", "")).strip()
    return cruise, ship_code, sample_number


def keys_invalid(row: Mapping[str, Any]) -> bool:
    cruise, ship_code, sample_number = _row_keys(row)
    return not cruise or not ship_code or not sample_number


def parse_egg_count(raw: Any) -> int | None:
    """Parse one egg count cell; invalid cells return None (never coerced to zero)."""
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if math.isnan(value) or value < 0 or value != int(value):
        return None
    return int(value)


def _pump_in_range(value: float) -> bool:
    return PUMP_SPEED_MIN_M3_PER_MIN <= value <= PUMP_SPEED_MAX_M3_PER_MIN


def assess_pump_readings(
    start_pump: float | None,
    stop_pump: float | None,
) -> tuple[int, dict[str, int]]:
    """
    Return QC_PUMP_INVALID flags and per-event detail counters (0 or 1 each).

    Detail keys: ``pump_out_of_bounds``, ``pump_ratio``.
    """
    detail = {"pump_out_of_bounds": 0, "pump_ratio": 0}
    flags = 0
    present = [p for p in (start_pump, stop_pump) if p is not None]

    if not present:
        flags |= QC_PUMP_INVALID
        detail["pump_out_of_bounds"] = 1
        return flags, detail

    for value in present:
        if not _pump_in_range(value):
            flags |= QC_PUMP_INVALID
            detail["pump_out_of_bounds"] = 1
            break

    in_range = [p for p in present if _pump_in_range(p)]
    if not in_range:
        flags |= QC_PUMP_INVALID
        detail["pump_out_of_bounds"] = 1

    if start_pump is not None and stop_pump is not None:
        lo = min(start_pump, stop_pump)
        hi = max(start_pump, stop_pump)
        if lo > 0 and hi / lo > PUMP_SPEED_MAX_START_STOP_RATIO:
            flags |= QC_PUMP_INVALID
            detail["pump_ratio"] = 1

    return flags, detail


def parse_row_egg_counts(row: Mapping[str, Any]) -> dict[str, int] | None:
    """Return taxon→count for all six categories, or None if any cell is invalid."""
    parsed: dict[str, int] = {}
    for col, taxon in EGG_CATEGORIES:
        count = parse_egg_count(row.get(col))
        if count is None:
            return None
        parsed[taxon] = count
    return parsed


def qc_flags_for_row(
    row: Mapping[str, Any],
    *,
    min_duration_min: float = DEFAULT_MIN_DURATION_MIN,
    max_duration_min: float = DEFAULT_MAX_DURATION_MIN,
    pump_qc_detail: dict[str, int] | None = None,
) -> int:
    flags = 0
    if keys_invalid(row):
        flags |= QC_KEY_INVALID

    if parse_row_egg_counts(row) is None:
        flags |= QC_COUNT_INVALID

    start_t = _parse_erddap_time(row.get("time"))
    stop_t = _parse_erddap_time(row.get("stop_time"))
    if stop_t is None:
        flags |= QC_MISSING_STOP_TIME
    elif start_t is not None and stop_t <= start_t:
        flags |= QC_REVERSED_TIME

    start_pump = _parse_float(row.get("start_pump_speed"))
    stop_pump = _parse_float(row.get("stop_pump_speed"))
    pump_flags, pump_detail = assess_pump_readings(start_pump, stop_pump)
    flags |= pump_flags
    if pump_qc_detail is not None and pump_flags:
        for key, inc in pump_detail.items():
            pump_qc_detail[key] += inc

    start_ok = _valid_lat_lon(_parse_float(row.get("latitude")), _parse_float(row.get("longitude")))
    stop_ok = _valid_lat_lon(
        _parse_float(row.get("stop_latitude")), _parse_float(row.get("stop_longitude"))
    )
    if not start_ok or not stop_ok:
        flags |= QC_COORD_INVALID

    if start_t and stop_t and flags & (QC_MISSING_STOP_TIME | QC_REVERSED_TIME) == 0:
        duration_min = (stop_t - start_t).total_seconds() / 60.0
        if duration_min < min_duration_min or duration_min > max_duration_min:
            flags |= QC_DURATION_OUT_OF_RANGE

    return flags


def volume_m3_for_row(row: Mapping[str, Any]) -> tuple[float | None, int]:
    """
    Effort volume (m³) and number of pump readings used (1 or 2).

    Uses the mean of all available positive pump speeds. When only one reading is
    valid, volume uses that single speed (no imputation of the missing stop/start value).
    """
    start_t = _parse_erddap_time(row.get("time"))
    stop_t = _parse_erddap_time(row.get("stop_time"))
    if start_t is None or stop_t is None or stop_t <= start_t:
        return None, 0
    start_pump = _parse_float(row.get("start_pump_speed"))
    stop_pump = _parse_float(row.get("stop_pump_speed"))
    pumps = [p for p in (start_pump, stop_pump) if p is not None and _pump_in_range(p)]
    if not pumps:
        return None, 0
    mean_pump = sum(pumps) / len(pumps)
    duration_min = (stop_t - start_t).total_seconds() / 60.0
    return mean_pump * duration_min, len(pumps)


def track_wkt(row: Mapping[str, Any]) -> str | None:
    lat0 = _parse_float(row.get("latitude"))
    lon0 = _parse_float(row.get("longitude"))
    lat1 = _parse_float(row.get("stop_latitude"))
    lon1 = _parse_float(row.get("stop_longitude"))
    if None in (lat0, lon0, lat1, lon1):
        return None
    return f"LINESTRING({lon0} {lat0}, {lon1} {lat1})"


def row_to_event(row: Mapping[str, Any], volume_m3: float, pump_readings_used: int) -> dict[str, Any]:
    cruise, ship_code, sample_number = _row_keys(row)
    event_id = make_event_id(cruise, ship_code, sample_number)
    start_t = _parse_erddap_time(row.get("time"))
    stop_t = _parse_erddap_time(row.get("stop_time"))
    lat = _parse_float(row.get("latitude"))
    lon = _parse_float(row.get("longitude"))
    stop_lat = _parse_float(row.get("stop_latitude"))
    stop_lon = _parse_float(row.get("stop_longitude"))
    if (
        start_t is None
        or stop_t is None
        or lat is None
        or lon is None
        or stop_lat is None
        or stop_lon is None
    ):
        raise ValueError(f"row_to_event called on row that did not pass QC: {event_id}")
    if pump_readings_used not in (1, 2):
        raise ValueError(f"pump_readings_used must be 1 or 2, got {pump_readings_used}")
    return {
        "event_id": event_id,
        "time": start_t.isoformat(),
        "lat": lat,
        "lon": lon,
        "stop_time": stop_t.isoformat(),
        "stop_lat": stop_lat,
        "stop_lon": stop_lon,
        "volume_m3": float(volume_m3),
        "pump_readings_used": pump_readings_used,
        "qc_flags": 0,
        "track_wkt": track_wkt(row),
    }


def row_to_occurrences(
    egg_counts: dict[str, int],
    event_id: str,
    volume_m3: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _col, taxon in EGG_CATEGORIES:
        count = egg_counts[taxon]
        status = "present" if count > 0 else "absent"
        density = count / volume_m3 if volume_m3 > 0 else None
        rows.append(
            {
                "event_id": event_id,
                "taxon": taxon,
                "count": count,
                "density": density,
                "occurrence_status": status,
                "life_stage": LIFE_STAGE_EGG,
                "zero_semantics": ZERO_SEMANTICS if count == 0 else None,
            }
        )
    return rows


def _empty_qc_report() -> dict[str, Any]:
    return {
        "events_read": 0,
        "dropped_by_rule": {label: 0 for label, _ in QC_RULE_LABELS},
        "pump_qc_detail": {
            "pump_out_of_bounds": 0,
            "pump_ratio": 0,
        },
        "dropped_rows": 0,
        "dropped_unique_total": 0,
        "events_kept": 0,
    }


def _record_drop(flags: int, dropped_by_rule: dict[str, int]) -> None:
    for label, bit in QC_RULE_LABELS:
        if bit and flags & bit:
            dropped_by_rule[label] += 1


def _validate_qc_report(report: dict[str, Any]) -> None:
    if report["events_read"] != report["events_kept"] + report["dropped_rows"]:
        raise ValueError(
            "QC report invariant failed: "
            f"events_read={report['events_read']} "
            f"events_kept={report['events_kept']} "
            f"dropped_rows={report['dropped_rows']}"
        )


@dataclass
class TransformResult:
    events: list[dict[str, Any]] = field(default_factory=list)
    counts: list[dict[str, Any]] = field(default_factory=list)
    qc_report: dict[str, Any] = field(default_factory=_empty_qc_report)


def transform_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    min_duration_min: float = DEFAULT_MIN_DURATION_MIN,
    max_duration_min: float = DEFAULT_MAX_DURATION_MIN,
) -> TransformResult:
    """
    Build events and counts only for rows that pass all QC rules.

    Failed events are omitted from events, counts (including explicit zeros), and DwC.
    """
    result = TransformResult()
    report = result.qc_report
    dropped_event_ids: set[str] = set()
    dropped_rows = 0
    kept_ids: set[str] = set()
    seen_event_ids: set[str] = set()
    duplicate_ids: set[str] = set()

    for row in rows:
        report["events_read"] += 1
        cruise, ship_code, sample_number = _row_keys(row)
        event_id = make_event_id(cruise, ship_code, sample_number)

        if not keys_invalid(row):
            if event_id in seen_event_ids:
                duplicate_ids.add(event_id)
            seen_event_ids.add(event_id)

        flags = qc_flags_for_row(
            row,
            min_duration_min=min_duration_min,
            max_duration_min=max_duration_min,
            pump_qc_detail=report["pump_qc_detail"],
        )
        if flags != 0:
            _record_drop(flags, report["dropped_by_rule"])
            dropped_rows += 1
            if not keys_invalid(row):
                dropped_event_ids.add(event_id)
            continue

        vol, pump_used = volume_m3_for_row(row)
        if vol is None or vol <= 0:
            report["dropped_by_rule"]["invalid_volume"] += 1
            dropped_rows += 1
            dropped_event_ids.add(event_id)
            continue

        egg_counts = parse_row_egg_counts(row)
        if egg_counts is None:
            raise ValueError("internal: egg counts missing after QC pass")

        event = row_to_event(row, float(vol), pump_used)
        kept_ids.add(event_id)
        result.events.append(event)
        result.counts.extend(row_to_occurrences(egg_counts, event_id, float(vol)))

    if duplicate_ids:
        ordered = ", ".join(sorted(duplicate_ids))
        raise ValueError(f"duplicate event_id(s): {ordered}")

    report["dropped_rows"] = dropped_rows
    report["dropped_unique_total"] = len(dropped_event_ids)
    report["events_kept"] = len(kept_ids)
    _validate_qc_report(report)
    return result
