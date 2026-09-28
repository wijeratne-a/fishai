"""QC, haul event construction, and catch long table for CPS trawl haul catch."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from fishai.ingestion.biology.cps_trawl.catch import (
    catch_row_invalid,
    catch_values_to_record,
    merge_catch_values,
    parse_catch_row,
)
from fishai.ingestion.biology.cps_trawl.constants import (
    MAX_TOW_DURATION_MIN,
    MIN_TOW_DURATION_MIN,
    NET_MOUTH_AREA_NULL_REASON,
    QC_CATCH_INVALID,
    QC_COORD_INVALID,
    QC_DURATION_INVALID,
    QC_HAUL_METADATA_CONFLICT,
    QC_KEY_INVALID,
    QC_RULE_LABELS,
    QC_TIME_INVALID,
)
from fishai.ingestion.physics.geo_distance import haversine_distance_nm

__all__ = [
    "TransformResult",
    "make_haul_id",
    "tow_distance_nm",
    "tow_duration_minutes",
    "transform_rows",
]


def make_haul_id(cruise: str, ship: str, haul: str | int) -> str:
    return f"CPSTrawl:{cruise}:{ship}:{haul}"


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


def _haul_keys(row: Mapping[str, Any]) -> tuple[str, str, str]:
    cruise = str(row.get("cruise", "")).strip()
    ship = str(row.get("ship", "")).strip()
    haul = str(row.get("haul", "")).strip()
    return cruise, ship, haul


def keys_invalid(row: Mapping[str, Any]) -> bool:
    cruise, ship, haul = _haul_keys(row)
    return not cruise or not ship or not haul


def tow_duration_minutes(start: datetime | None, haulback: datetime | None) -> float | None:
    if start is None or haulback is None:
        return None
    seconds = (haulback - start).total_seconds()
    return seconds / 60.0


def tow_distance_nm(
    start_lat: float | None,
    start_lon: float | None,
    stop_lat: float | None,
    stop_lon: float | None,
) -> float | None:
    if None in (start_lat, start_lon, stop_lat, stop_lon):
        return None
    return haversine_distance_nm(start_lat, start_lon, stop_lat, stop_lon)


def _haul_metadata_signature(row: Mapping[str, Any]) -> tuple[Any, ...]:
    start_t = _parse_erddap_time(row.get("time"))
    haulback_t = _parse_erddap_time(row.get("haulback_time"))
    return (
        start_t.isoformat() if start_t else None,
        haulback_t.isoformat() if haulback_t else None,
        _parse_float(row.get("latitude")),
        _parse_float(row.get("longitude")),
        _parse_float(row.get("stop_latitude")),
        _parse_float(row.get("stop_longitude")),
        _parse_float(row.get("ship_spd_through_water")),
    )


def qc_flags_for_haul(rows: list[Mapping[str, Any]]) -> int:
    if not rows:
        return QC_KEY_INVALID
    flags = 0
    if keys_invalid(rows[0]):
        flags |= QC_KEY_INVALID
        return flags

    sig0 = _haul_metadata_signature(rows[0])
    for row in rows[1:]:
        if _haul_metadata_signature(row) != sig0:
            flags |= QC_HAUL_METADATA_CONFLICT
            break

    row = rows[0]
    lat = _parse_float(row.get("latitude"))
    lon = _parse_float(row.get("longitude"))
    if lat is None or lon is None or not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
        flags |= QC_COORD_INVALID

    start_t = _parse_erddap_time(row.get("time"))
    haulback_t = _parse_erddap_time(row.get("haulback_time"))
    if start_t is None or haulback_t is None:
        flags |= QC_TIME_INVALID
    elif haulback_t <= start_t:
        flags |= QC_TIME_INVALID
    else:
        duration = tow_duration_minutes(start_t, haulback_t)
        if duration is None or duration < MIN_TOW_DURATION_MIN or duration > MAX_TOW_DURATION_MIN:
            flags |= QC_DURATION_INVALID

    for row in rows:
        if catch_row_invalid(row):
            flags |= QC_CATCH_INVALID
            break

    return flags


def haul_row_to_event(row: Mapping[str, Any], duration_min: float) -> dict[str, Any]:
    cruise, ship, haul = _haul_keys(row)
    haul_id = make_haul_id(cruise, ship, haul)
    start_t = _parse_erddap_time(row.get("time"))
    haulback_t = _parse_erddap_time(row.get("haulback_time"))
    if start_t is None or haulback_t is None:
        raise ValueError(f"haul_row_to_event called on row that did not pass QC: {haul_id}")

    lat = _parse_float(row.get("latitude"))
    lon = _parse_float(row.get("longitude"))
    stop_lat = _parse_float(row.get("stop_latitude"))
    stop_lon = _parse_float(row.get("stop_longitude"))
    distance = tow_distance_nm(lat, lon, stop_lat, stop_lon)

    return {
        "haul_id": haul_id,
        "cruise": cruise,
        "ship": ship,
        "haul": int(haul) if haul.isdigit() else haul,
        "survey_id": cruise,
        "time": start_t.isoformat(),
        "haulback_time": haulback_t.isoformat(),
        "lat": lat,
        "lon": lon,
        "stop_lat": stop_lat,
        "stop_lon": stop_lon,
        "tow_duration_min": float(duration_min),
        "tow_distance_nm": distance,
        "tow_distance_nm_null_reason": None if distance is not None else "stop_coordinates_missing",
        "ship_spd_through_water_kn": _parse_float(row.get("ship_spd_through_water")),
        "ship_spd_null_reason": None
        if _parse_float(row.get("ship_spd_through_water")) is not None
        else "missing_in_source_row",
        "net_mouth_area_m2": None,
        "net_mouth_area_m2_null_reason": NET_MOUTH_AREA_NULL_REASON,
        "surface_temp_c": _parse_float(row.get("surface_temp")),
        "surface_temp_method": str(row.get("surface_temp_method") or "").strip() or None,
    }


def _empty_qc_report() -> dict[str, Any]:
    return {
        "catch_rows_read": 0,
        "hauls_read": 0,
        "hauls_kept": 0,
        "catch_rows_kept": 0,
        "dropped_by_rule": {label: 0 for label, _ in QC_RULE_LABELS},
        "units_rows_skipped": 0,
        "zero_frame_evidence_path": "config/cps_trawl_zero_frame_evidence.yaml",
        "zero_frame_investigation": {
            "empty_haul_metadata_dataset_on_erddap": False,
            "animalia_only_hauls_in_catch_table": None,
            "specimen_or_lf_hauls_missing_from_catch": 0,
            "notes": (
                "FRDCPSTrawlLHHaulCatch only lists species caught; implied zero-catch "
                "requires a verified complete haul frame (see README)."
            ),
        },
    }


def _record_drop(flags: int, dropped_by_rule: dict[str, int]) -> None:
    for label, bit in QC_RULE_LABELS:
        if bit and flags & bit:
            dropped_by_rule[label] += 1


@dataclass
class TransformResult:
    hauls: list[dict[str, Any]] = field(default_factory=list)
    catch: list[dict[str, Any]] = field(default_factory=list)
    qc_report: dict[str, Any] = field(default_factory=_empty_qc_report)


def transform_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    units_rows_skipped: int = 0,
) -> TransformResult:
    """Build haul and catch tables; drop hauls that fail QC."""
    result = TransformResult()
    report = result.qc_report
    report["units_rows_skipped"] = units_rows_skipped

    grouped: dict[str, list[Mapping[str, Any]]] = {}
    haul_order: list[str] = []

    for row in rows:
        report["catch_rows_read"] += 1
        if keys_invalid(row):
            _record_drop(QC_KEY_INVALID, report["dropped_by_rule"])
            continue
        cruise, ship, haul = _haul_keys(row)
        haul_id = make_haul_id(cruise, ship, haul)
        if haul_id not in grouped:
            grouped[haul_id] = []
            haul_order.append(haul_id)
        grouped[haul_id].append(row)

    animalia_only = 0
    for haul_id in haul_order:
        haul_rows = grouped[haul_id]
        report["hauls_read"] += 1
        flags = qc_flags_for_haul(haul_rows)
        if flags:
            _record_drop(flags, report["dropped_by_rule"])
            continue

        row = haul_rows[0]
        start_t = _parse_erddap_time(row.get("time"))
        haulback_t = _parse_erddap_time(row.get("haulback_time"))
        duration = tow_duration_minutes(start_t, haulback_t)
        if duration is None:
            _record_drop(QC_TIME_INVALID, report["dropped_by_rule"])
            continue

        by_species: dict[str, list] = {}
        for catch_row in haul_rows:
            parsed = parse_catch_row(catch_row)
            if parsed is None:
                continue
            by_species.setdefault(parsed.species, []).append(parsed)

        species_seen: set[str] = set()
        for species, parsed_rows in sorted(by_species.items()):
            merged = merge_catch_values(parsed_rows)
            species_seen.add(species)
            result.catch.append(catch_values_to_record(haul_id, merged))
            report["catch_rows_kept"] += 1

        animalia_only_haul = species_seen == {"Animalia"}
        if animalia_only_haul:
            animalia_only += 1
        event = haul_row_to_event(row, duration)
        event["animalia_only_haul"] = animalia_only_haul
        event["zero_frame_exclude_reason"] = (
            "animalia_only_undocumented" if animalia_only_haul else None
        )
        result.hauls.append(event)

    report["hauls_kept"] = len(result.hauls)
    report["zero_frame_investigation"]["animalia_only_hauls_in_catch_table"] = animalia_only
    return result
