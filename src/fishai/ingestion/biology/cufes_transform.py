"""QC, event construction, and occurrence wide-to-long for CUFES."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

from fishai.ingestion.biology.cufes_constants import (
    DEFAULT_MAX_DURATION_MIN,
    DEFAULT_MIN_DURATION_MIN,
    EGG_CATEGORIES,
    LIFE_STAGE_EGG,
    PUMP_SPEED_UNITS,
    QC_COORD_INVALID,
    QC_DURATION_OUT_OF_RANGE,
    QC_MISSING_STOP_TIME,
    QC_PUMP_INVALID,
    QC_REVERSED_TIME,
    ZERO_SEMANTICS,
)


def make_event_id(cruise: str, ship_code: str, sample_number: str | int) -> str:
    return f"CUFES:{cruise}:{ship_code}:{sample_number}"


def make_sample_id(cruise: str, ship_code: str, sample_number: str | int) -> str:
    return make_event_id(cruise, ship_code, sample_number)


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

    Pump speed units per ERDDAP ``erdCalCOFIcufes.das``: ``M^3 per minute`` ({PUMP_SPEED_UNITS}).
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


def row_to_event(row: Mapping[str, Any], qc_flags: int) -> dict[str, Any]:
    cruise = str(row.get("cruise", "")).strip()
    ship_code = str(row.get("ship_code", "")).strip()
    sample_number = str(row.get("sample_number", "")).strip()
    sample_id = make_sample_id(cruise, ship_code, sample_number)
    start_t = _parse_erddap_time(row.get("time"))
    stop_t = _parse_erddap_time(row.get("stop_time"))
    vol = volume_m3_for_row(row)
    return {
        "sample_id": sample_id,
        "event_id": sample_id,
        "cruise": cruise,
        "ship_code": ship_code,
        "sample_number": sample_number,
        "start_time": start_t.isoformat() if start_t else None,
        "stop_time": stop_t.isoformat() if stop_t else None,
        "start_latitude": _parse_float(row.get("latitude")),
        "start_longitude": _parse_float(row.get("longitude")),
        "stop_latitude": _parse_float(row.get("stop_latitude")),
        "stop_longitude": _parse_float(row.get("stop_longitude")),
        "volume_m3": vol,
        "track_wkt": track_wkt(row),
        "qc_flags": qc_flags,
        "pump_speed_units": PUMP_SPEED_UNITS,
    }


def row_to_occurrences(row: Mapping[str, Any], sample_id: str, volume_m3: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for col, taxon in EGG_CATEGORIES:
        raw = row.get(col)
        try:
            count = int(float(str(raw).strip())) if raw is not None and str(raw).strip() else 0
        except ValueError:
            count = 0
        status = "present" if count > 0 else "absent"
        density = (count / volume_m3) if volume_m3 and volume_m3 > 0 else None
        rows.append(
            {
                "sample_id": sample_id,
                "taxon": taxon,
                "count": count,
                "density": density,
                "occurrence_status": status,
                "life_stage": LIFE_STAGE_EGG,
                "zero_semantics": ZERO_SEMANTICS if count == 0 else None,
            }
        )
    return rows


def transform_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    min_duration_min: float = DEFAULT_MIN_DURATION_MIN,
    max_duration_min: float = DEFAULT_MAX_DURATION_MIN,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return (events, counts) after QC; failed samples are omitted entirely."""
    events: list[dict[str, Any]] = []
    counts: list[dict[str, Any]] = []
    for row in rows:
        flags = qc_flags_for_row(
            row, min_duration_min=min_duration_min, max_duration_min=max_duration_min
        )
        if flags != 0:
            continue
        event = row_to_event(row, flags)
        vol = event.get("volume_m3")
        if vol is None or vol <= 0:
            continue
        events.append(event)
        counts.extend(row_to_occurrences(row, event["sample_id"], float(vol)))
    return events, counts
