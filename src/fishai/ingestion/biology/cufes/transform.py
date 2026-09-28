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
    QC_COORD_INVALID,
    QC_DURATION_OUT_OF_RANGE,
    QC_MISSING_STOP_TIME,
    QC_PUMP_INVALID,
    QC_REVERSED_TIME,
    QC_RULE_LABELS,
    ZERO_SEMANTICS,
)

__all__ = [
    "TransformResult",
    "make_event_id",
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


def qc_flags_for_row(
    row: Mapping[str, Any],
    *,
    min_duration_min: float = DEFAULT_MIN_DURATION_MIN,
    max_duration_min: float = DEFAULT_MAX_DURATION_MIN,
) -> int:
    flags = 0
    start_t = _parse_erddap_time(row.get("time"))
    stop_t = _parse_erddap_time(row.get("stop_time"))
    if stop_t is None:
        flags |= QC_MISSING_STOP_TIME
    elif start_t is not None and stop_t <= start_t:
        flags |= QC_REVERSED_TIME

    start_pump = _parse_float(row.get("start_pump_speed"))
    stop_pump = _parse_float(row.get("stop_pump_speed"))
    pumps = [p for p in (start_pump, stop_pump) if p is not None]
    if not pumps or any(p <= 0 for p in pumps):
        flags |= QC_PUMP_INVALID

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


def volume_m3_for_row(row: Mapping[str, Any]) -> float | None:
    """
    Effort volume (m³) = mean(start_pump_speed, stop_pump_speed) [m³/min] × duration [min].

    Pump speed units per ERDDAP ``erdCalCOFIcufes.das``: ``M^3 per minute``.
    """
    start_t = _parse_erddap_time(row.get("time"))
    stop_t = _parse_erddap_time(row.get("stop_time"))
    if start_t is None or stop_t is None or stop_t <= start_t:
        return None
    start_pump = _parse_float(row.get("start_pump_speed"))
    stop_pump = _parse_float(row.get("stop_pump_speed"))
    pumps = [p for p in (start_pump, stop_pump) if p is not None and p > 0]
    if not pumps:
        return None
    mean_pump = sum(pumps) / len(pumps)
    duration_min = (stop_t - start_t).total_seconds() / 60.0
    return mean_pump * duration_min


def track_wkt(row: Mapping[str, Any]) -> str | None:
    lat0 = _parse_float(row.get("latitude"))
    lon0 = _parse_float(row.get("longitude"))
    lat1 = _parse_float(row.get("stop_latitude"))
    lon1 = _parse_float(row.get("stop_longitude"))
    if None in (lat0, lon0, lat1, lon1):
        return None
    return f"LINESTRING({lon0} {lat0}, {lon1} {lat1})"


def row_to_event(row: Mapping[str, Any]) -> dict[str, Any]:
    cruise = str(row.get("cruise", "")).strip()
    ship_code = str(row.get("ship_code", "")).strip()
    sample_number = str(row.get("sample_number", "")).strip()
    event_id = make_event_id(cruise, ship_code, sample_number)
    start_t = _parse_erddap_time(row.get("time"))
    stop_t = _parse_erddap_time(row.get("stop_time"))
    lat = _parse_float(row.get("latitude"))
    lon = _parse_float(row.get("longitude"))
    stop_lat = _parse_float(row.get("stop_latitude"))
    stop_lon = _parse_float(row.get("stop_longitude"))
    vol = volume_m3_for_row(row)
    if (
        start_t is None
        or stop_t is None
        or lat is None
        or lon is None
        or stop_lat is None
        or stop_lon is None
        or vol is None
    ):
        raise ValueError(f"row_to_event called on row that did not pass QC: {event_id}")
    return {
        "event_id": event_id,
        "time": start_t.isoformat(),
        "lat": lat,
        "lon": lon,
        "stop_time": stop_t.isoformat(),
        "stop_lat": stop_lat,
        "stop_lon": stop_lon,
        "volume_m3": float(vol),
        "qc_flags": 0,
        "track_wkt": track_wkt(row),
    }


def row_to_occurrences(row: Mapping[str, Any], event_id: str, volume_m3: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for col, taxon in EGG_CATEGORIES:
        raw = row.get(col)
        try:
            count = int(float(str(raw).strip())) if raw is not None and str(raw).strip() else 0
        except ValueError:
            count = 0
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
        "dropped_unique_total": 0,
        "events_kept": 0,
    }


def _record_drop(flags: int, dropped_by_rule: dict[str, int]) -> None:
    for label, bit in QC_RULE_LABELS:
        if flags & bit:
            dropped_by_rule[label] += 1


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
    dropped_ids: set[str] = set()
    kept_ids: set[str] = set()

    for row in rows:
        report["events_read"] += 1
        cruise = str(row.get("cruise", "")).strip()
        ship_code = str(row.get("ship_code", "")).strip()
        sample_number = str(row.get("sample_number", "")).strip()
        event_id = make_event_id(cruise, ship_code, sample_number)

        flags = qc_flags_for_row(
            row, min_duration_min=min_duration_min, max_duration_min=max_duration_min
        )
        if flags != 0:
            _record_drop(flags, report["dropped_by_rule"])
            dropped_ids.add(event_id)
            continue

        vol = volume_m3_for_row(row)
        if vol is None or vol <= 0:
            report["dropped_by_rule"]["invalid_volume"] += 1
            dropped_ids.add(event_id)
            continue

        event = row_to_event(row)
        kept_ids.add(event_id)
        result.events.append(event)
        result.counts.extend(row_to_occurrences(row, event_id, float(vol)))

    report["dropped_unique_total"] = len(dropped_ids)
    report["events_kept"] = len(kept_ids)
    assert report["events_read"] == report["events_kept"] + report["dropped_unique_total"]
    return result
