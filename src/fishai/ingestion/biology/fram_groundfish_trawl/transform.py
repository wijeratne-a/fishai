"""QC and tow-level tables for FRAM groundfish pelagic bycatch (sardine/anchovy)."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

from fishai.ingestion.biology.fram_groundfish_trawl.constants import (
    PELAGIC_BYCATCH_BIAS_NOTE,
    PRESENCE_ONLY_BYCATCH_REASON,
    QC_COORD_INVALID,
    QC_CPUE_MISSING,
    QC_HAUL_JOIN_MISSING,
    QC_PERFORMANCE_EXCLUDED,
    QC_RULE_LABELS,
    QC_SPECIES_INVALID,
    QC_TRAWL_ID_INVALID,
    QC_YEAR_MISMATCH,
    SCIENTIFIC_NAME_FIELD,
    TARGET_SPECIES,
    TARGET_SPECIES_ITIS_TSN,
)
from fishai.ingestion.biology.fram_groundfish_trawl.trawl_id import survey_year_from_trawl_id

logger = logging.getLogger(__name__)

__all__ = ["TransformResult", "make_tow_id", "transform_rows", "format_qc_summary"]

EXCLUDED_PERFORMANCE = frozenset({"Unusable", "Aborted"})


def make_tow_id(trawl_id: int | str) -> str:
    return f"FRAMGroundfishTrawl:{trawl_id}"


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


def _parse_int(value: Any) -> int | None:
    f = _parse_float(value)
    if f is None:
        return None
    return int(f)


def _valid_lat_lon(lat: float | None, lon: float | None) -> bool:
    return (
        lat is not None
        and lon is not None
        and -90.0 <= lat <= 90.0
        and -180.0 <= lon <= 180.0
    )


def _empty_qc_report() -> dict[str, Any]:
    return {
        "catch_rows_read": 0,
        "catch_rows_kept": 0,
        "hauls_indexed": 0,
        "tows_kept": 0,
        "dropped_by_rule": {label: 0 for label, _ in QC_RULE_LABELS},
        "pelagic_bycatch_bias": PELAGIC_BYCATCH_BIAS_NOTE,
        "presence_only": True,
        "implied_zeros_emitted": 0,
    }


def _record_drop(flags: int, dropped_by_rule: dict[str, int]) -> None:
    for label, bit in QC_RULE_LABELS:
        if bit and flags & bit:
            dropped_by_rule[label] += 1


def _haul_index(hauls: Iterable[Mapping[str, Any]]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for row in hauls:
        tid = _parse_int(row.get("trawl_id"))
        if tid is None:
            continue
        out[tid] = dict(row)
    return out


def _haul_to_event(haul: Mapping[str, Any]) -> dict[str, Any]:
    trawl_id = _parse_int(haul.get("trawl_id"))
    assert trawl_id is not None
    lat = _parse_float(haul.get("latitude_dd"))
    lon = _parse_float(haul.get("longitude_dd"))
    return {
        "tow_id": make_tow_id(trawl_id),
        "trawl_id": trawl_id,
        "survey_year": survey_year_from_trawl_id(trawl_id),
        "vessel": str(haul.get("vessel") or "").strip() or None,
        "tow": _parse_int(haul.get("tow")),
        "project": str(haul.get("project") or "").strip() or None,
        "performance": str(haul.get("performance") or "").strip() or None,
        "datetime_utc": str(haul.get("datetime_utc_iso") or "").strip() or None,
        "area_swept_ha": _parse_float(haul.get("area_swept_ha_der")),
        "depth_m": _parse_float(haul.get("depth_hi_prec_m")),
        "lat": lat,
        "lon": lon,
        "gear_start_lat": _parse_float(haul.get("gear_start_latitude_dd")),
        "gear_start_lon": _parse_float(haul.get("gear_start_longitude_dd")),
        "gear_end_lat": _parse_float(haul.get("gear_end_latitude_dd")),
        "gear_end_lon": _parse_float(haul.get("gear_end_longitude_dd")),
        "sampling_start_hhmmss": str(haul.get("sampling_start_hhmmss") or "").strip() or None,
        "sampling_end_hhmmss": str(haul.get("sampling_end_hhmmss") or "").strip() or None,
        "station_invalid": _parse_int(haul.get("station_invalid")),
    }


@dataclass
class TransformResult:
    hauls: list[dict[str, Any]] = field(default_factory=list)
    catch: list[dict[str, Any]] = field(default_factory=list)
    qc_report: dict[str, Any] = field(default_factory=_empty_qc_report)


def transform_rows(
    catch_rows: Iterable[Mapping[str, Any]],
    haul_rows: Iterable[Mapping[str, Any]],
) -> TransformResult:
    """Join catch to haul effort; drop rows that fail QC.

    Only positive sardine/anchovy bycatch rows are present in ``catch_fact`` — no implied
    zeros (see ``PELAGIC_BYCATCH_BIAS_NOTE``).
    """
    result = TransformResult()
    report = result.qc_report
    haul_by_id = _haul_index(haul_rows)
    report["hauls_indexed"] = len(haul_by_id)

    tow_events: dict[str, dict[str, Any]] = {}
    target_set = set(TARGET_SPECIES)

    for row in catch_rows:
        report["catch_rows_read"] += 1
        flags = 0
        trawl_id = _parse_int(row.get("trawl_id"))
        if trawl_id is None:
            flags |= QC_TRAWL_ID_INVALID
            _record_drop(flags, report["dropped_by_rule"])
            continue

        species = str(row.get(SCIENTIFIC_NAME_FIELD) or "").strip()
        if species not in target_set:
            flags |= QC_SPECIES_INVALID
            _record_drop(flags, report["dropped_by_rule"])
            continue

        derived_year = survey_year_from_trawl_id(trawl_id)
        if derived_year is None:
            flags |= QC_YEAR_MISMATCH
            _record_drop(flags, report["dropped_by_rule"])
            continue

        haul = haul_by_id.get(trawl_id)
        if haul is None:
            flags |= QC_HAUL_JOIN_MISSING
            _record_drop(flags, report["dropped_by_rule"])
            continue

        performance = str(row.get("performance") or haul.get("performance") or "").strip()
        if performance in EXCLUDED_PERFORMANCE:
            flags |= QC_PERFORMANCE_EXCLUDED
            _record_drop(flags, report["dropped_by_rule"])
            continue

        event = _haul_to_event(haul)
        if not _valid_lat_lon(event.get("lat"), event.get("lon")):
            flags |= QC_COORD_INVALID
            _record_drop(flags, report["dropped_by_rule"])
            continue

        cpue = _parse_float(row.get("cpue_kg_per_ha_der"))
        cpue_missing = cpue is None
        if cpue_missing:
            flags |= QC_CPUE_MISSING
            # Keep row but flag; corroboration can tolerate sparse CPUE gaps.

        tow_id = make_tow_id(trawl_id)
        if tow_id not in tow_events:
            tow_events[tow_id] = event
            result.hauls.append(event)

        catch_rec = {
            "tow_id": tow_id,
            "trawl_id": trawl_id,
            "survey_year": derived_year,
            "scientific_name": species,
            "itis_tsn": TARGET_SPECIES_ITIS_TSN.get(species),
            "total_catch_wt_kg": _parse_float(row.get("total_catch_wt_kg")),
            "total_catch_numbers": _parse_float(row.get("total_catch_numbers")),
            "cpue_kg_per_ha": cpue,
            "cpue_kg_per_ha_null_reason": "missing_in_source_row" if cpue_missing else None,
            "depth_m": _parse_float(row.get("depth_m")),
            "performance": performance or None,
            "presence_only": True,
            "presence_only_reason": PRESENCE_ONLY_BYCATCH_REASON,
            "qc_flags": flags,
        }
        result.catch.append(catch_rec)
        report["catch_rows_kept"] += 1
        if cpue_missing:
            _record_drop(QC_CPUE_MISSING, report["dropped_by_rule"])

    report["tows_kept"] = len(result.hauls)
    result.hauls.sort(key=lambda h: (h.get("survey_year") or 0, h.get("trawl_id") or 0))
    result.catch.sort(key=lambda c: (c.get("survey_year") or 0, c.get("trawl_id") or 0, c.get("scientific_name") or ""))
    return result


def format_qc_summary(report: dict[str, Any]) -> str:
    dropped = report.get("dropped_by_rule") or {}
    parts = [
        f"catch_rows_read={report.get('catch_rows_read', 0)}",
        f"catch_rows_kept={report.get('catch_rows_kept', 0)}",
        f"tows_kept={report.get('tows_kept', 0)}",
    ]
    for key, count in sorted(dropped.items()):
        if count:
            parts.append(f"{key}={count}")
    return "qc " + " ".join(parts)
