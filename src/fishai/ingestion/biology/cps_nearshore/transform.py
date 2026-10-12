"""QC, set event construction, and catch long table for CPS nearshore set catch."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from fishai.ingestion.biology.cps_nearshore.catch import (
    catch_row_invalid,
    catch_row_unparseable,
    catch_values_to_record,
    parse_catch_row,
)
from fishai.ingestion.biology.cps_nearshore.constants import (
    EFFORT_DURATION_NULL_REASON,
    QC_CATCH_INVALID,
    QC_COORD_INVALID,
    QC_KEY_INVALID,
    QC_RULE_LABELS,
    QC_SET_METADATA_CONFLICT,
    QC_TIME_INVALID,
)

logger = logging.getLogger(__name__)

__all__ = [
    "TransformResult",
    "make_set_id",
    "transform_rows",
    "format_qc_summary",
]


def make_set_id(cruise: str, ship: str, set_no: str | int) -> str:
    return f"CPSNearshore:{cruise}:{ship}:{set_no}"


def _parse_erddap_time(value: Any) -> datetime | None:
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
    return (
        lat is not None
        and lon is not None
        and -90.0 <= lat <= 90.0
        and -180.0 <= lon <= 180.0
    )


@dataclass
class TransformResult:
    sets: list[dict[str, Any]] = field(default_factory=list)
    catch: list[dict[str, Any]] = field(default_factory=list)
    qc_flags: dict[str, int] = field(default_factory=dict)
    dropped_sets: int = 0


def transform_rows(rows: Iterable[Mapping[str, Any]]) -> TransformResult:
    """Build per-set event records and the long catch table.

    One output set record per unique (cruise, ship, set); one catch record per
    input row that survives QC. Sets with any QC flag are dropped entirely.
    """
    result = TransformResult()
    set_accum: dict[str, dict[str, Any]] = {}
    dropped: set[str] = set()

    def flag(label: str) -> None:
        result.qc_flags[label] = result.qc_flags.get(label, 0) + 1

    def drop_set(set_id: str) -> None:
        if set_id not in dropped:
            dropped.add(set_id)
            result.dropped_sets += 1
        set_accum.pop(set_id, None)

    for row in rows:
        cruise = str(row.get("cruise") or "").strip()
        ship = str(row.get("ship") or "").strip()
        set_no = str(row.get("set") or "").strip()
        if not cruise or not ship or not set_no:
            flag("key_invalid")
            continue
        set_id = make_set_id(cruise, ship, set_no)
        if set_id in dropped:
            continue

        lat = _parse_float(row.get("latitude"))
        lon = _parse_float(row.get("longitude"))
        if not _valid_lat_lon(lat, lon):
            flag("coord_invalid")
            drop_set(set_id)
            continue

        when = _parse_erddap_time(row.get("time"))
        if when is None:
            flag("time_invalid")
            drop_set(set_id)
            continue

        if catch_row_unparseable(row):
            flag("catch_invalid")
            continue
        parsed = parse_catch_row(row)
        if parsed is None or catch_row_invalid(row):
            flag("catch_invalid")
            continue

        existing = set_accum.get(set_id)
        meta = {
            "set_id": set_id,
            "cruise": cruise,
            "ship": ship,
            "set_number": set_no,
            "time_utc": when.isoformat(),
            "latitude": lat,
            "longitude": lon,
            "state": str(row.get("state") or "").strip() or None,
            "gear_type": str(row.get("gearType") or "").strip() or None,
            # Purse-seine sets are point events: no tow duration/distance.
            "effort_duration_min": None,
            "effort_duration_null_reason": EFFORT_DURATION_NULL_REASON,
        }
        if existing is not None:
            for key in ("time_utc", "latitude", "longitude"):
                if existing[key] != meta[key]:
                    flag("set_metadata_conflict")
                    logger.warning("set metadata conflict for %s on %s", set_id, key)
                    drop_set(set_id)
                    existing = None
                    break
            if existing is None:
                continue
        else:
            set_accum[set_id] = meta

        result.catch.append(catch_values_to_record(set_id, parsed))

    # Drop catch rows whose set was dropped.
    live = set(set_accum)
    result.catch = [c for c in result.catch if c["set_id"] in live]
    result.sets = [set_accum[k] for k in sorted(live)]

    for bit_label, _bit in QC_RULE_LABELS:
        result.qc_flags.setdefault(bit_label, 0)
    return result


def format_qc_summary(result: TransformResult) -> str:
    parts = [f"sets={len(result.sets)}", f"catch_rows={len(result.catch)}"]
    parts.extend(f"{label}={result.qc_flags.get(label, 0)}" for label, _ in QC_RULE_LABELS)
    parts.append(f"dropped_sets={result.dropped_sets}")
    return " ".join(parts)
