"""QC, event construction, and occurrence wide-to-long for CUFES."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from fishai.ingestion.biology.cufes.constants import (
    DEFAULT_MAX_DURATION_MIN,
    EGG_CATEGORIES,
    LIFE_STAGE_EGG,
    MIN_DURATION_BOTH_SECONDS_NONZERO_MIN,
    MIN_DURATION_WHOLE_MINUTE_MIN,
    PUMP_SPEED_MAX_M3_PER_MIN,
    PUMP_SPEED_MAX_START_STOP_RATIO,
    PUMP_SPEED_MIN_M3_PER_MIN,
    QC_COORD_INVALID,
    QC_COUNT_INVALID,
    QC_DURATION_OUT_OF_RANGE,
    QC_DURATION_SHORT_MINUTE,
    QC_DURATION_SHORT_SECOND,
    QC_KEY_INVALID,
    QC_MISSING_STOP_TIME,
    QC_NO_TAXA_SAMPLED,
    QC_PUMP_INVALID,
    QC_REVERSED_TIME,
    QC_RULE_LABELS,
    SHORT_EVENT_THRESHOLD_MIN,
    SPEED_REVIEW_THRESHOLD_KN,
    ZERO_SEMANTICS,
)
from fishai.ingestion.biology.cufes.eggs import classify_egg_row, egg_cell_invalid, egg_cell_not_sampled
from fishai.ingestion.biology.cufes.geo import implied_speed_knots

__all__ = [
    "TransformResult",
    "make_event_id",
    "parse_egg_count",
    "qc_flags_for_row",
    "transform_rows",
    "volume_m3_for_row",
]

EGG_CELL_QC_DOCUMENTATION: dict[str, str] = {
    "erddap_not_sampled": (
        "A taxon was not sampled when the cell is missing (None), an empty string after "
        "ASCII strip, or the literal text NaN (case-insensitive). ERDDAP tabledap CSV "
        "writes missing values as an empty field or NaN; both are treated as not sampled."
    ),
    "invalid_whole_event": (
        "Any other cell value (non-numeric text, negative numbers, non-integer fractions, "
        "or whitespace-only content that does not strip to empty) sets QC_COUNT_INVALID "
        "and drops the entire event."
    ),
}


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
    """Parse one egg count cell when sampled; invalid cells return None (never coerced to zero)."""
    if egg_cell_not_sampled(raw):
        return None
    if egg_cell_invalid(raw):
        return None
    return int(float(str(raw).strip()))


def _pump_in_range(value: float) -> bool:
    return PUMP_SPEED_MIN_M3_PER_MIN <= value <= PUMP_SPEED_MAX_M3_PER_MIN


def assess_pump_readings(
    start_pump: float | None,
    stop_pump: float | None,
) -> tuple[int, dict[str, int]]:
    """
    Return QC_PUMP_INVALID flags and per-event detail counters (0 or 1 each).

    Detail keys: ``pump_missing``, ``pump_out_of_bounds``, ``pump_ratio``.
    """
    detail = {"pump_missing": 0, "pump_out_of_bounds": 0, "pump_ratio": 0}
    flags = 0
    present = [p for p in (start_pump, stop_pump) if p is not None]

    if not present:
        flags |= QC_PUMP_INVALID
        detail["pump_missing"] = 1
        return flags, detail

    for value in present:
        if not _pump_in_range(value):
            flags |= QC_PUMP_INVALID
            detail["pump_out_of_bounds"] = 1
            break

    if start_pump is not None and stop_pump is not None:
        lo = min(start_pump, stop_pump)
        hi = max(start_pump, stop_pump)
        if lo > 0 and hi / lo > PUMP_SPEED_MAX_START_STOP_RATIO:
            flags |= QC_PUMP_INVALID
            detail["pump_ratio"] = 1

    return flags, detail


def _min_duration_required_minutes(start_t: datetime, stop_t: datetime) -> float:
    if start_t.second != 0 and stop_t.second != 0:
        return MIN_DURATION_BOTH_SECONDS_NONZERO_MIN
    return MIN_DURATION_WHOLE_MINUTE_MIN


def duration_qc_flags(
    start_t: datetime | None,
    stop_t: datetime | None,
    *,
    max_duration_min: float = DEFAULT_MAX_DURATION_MIN,
) -> tuple[int, float | None]:
    """Return duration QC bitmask and duration in minutes (when both times are valid)."""
    if start_t is None or stop_t is None or stop_t <= start_t:
        return 0, None
    duration_min = (stop_t - start_t).total_seconds() / 60.0
    if duration_min > max_duration_min:
        return QC_DURATION_OUT_OF_RANGE, duration_min
    min_required = _min_duration_required_minutes(start_t, stop_t)
    if duration_min < min_required:
        if min_required == MIN_DURATION_BOTH_SECONDS_NONZERO_MIN:
            return QC_DURATION_SHORT_SECOND, duration_min
        return QC_DURATION_SHORT_MINUTE, duration_min
    return 0, duration_min


def egg_qc_flags(row: Mapping[str, Any]) -> tuple[int, dict[str, int] | None]:
    """Return egg-related QC flags and sampled taxon counts when the row is kept."""
    state = classify_egg_row(row)
    if state.invalid:
        return QC_COUNT_INVALID, None
    if state.all_not_sampled:
        return QC_NO_TAXA_SAMPLED, None
    return 0, state.sampled


def qc_flags_for_row(
    row: Mapping[str, Any],
    *,
    max_duration_min: float = DEFAULT_MAX_DURATION_MIN,
    pump_qc_detail: dict[str, int] | None = None,
) -> int:
    flags = 0
    if keys_invalid(row):
        flags |= QC_KEY_INVALID

    egg_flags, _ = egg_qc_flags(row)
    flags |= egg_flags

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
        dur_flags, _ = duration_qc_flags(start_t, stop_t, max_duration_min=max_duration_min)
        flags |= dur_flags

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


def row_to_event(
    row: Mapping[str, Any],
    volume_m3: float,
    pump_readings_used: int,
    duration_min: float,
) -> dict[str, Any]:
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
    implied_speed = implied_speed_knots(lat, lon, stop_lat, stop_lon, duration_min)
    speed_review = implied_speed is not None and implied_speed > SPEED_REVIEW_THRESHOLD_KN
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
        "duration_min": float(duration_min),
        "short_event": duration_min < SHORT_EVENT_THRESHOLD_MIN,
        "implied_speed_kn": implied_speed,
        "speed_review_flag": speed_review,
        "qc_flags": 0,
        "track_wkt": track_wkt(row),
    }


def row_to_occurrences(
    sampled_counts: dict[str, int],
    event_id: str,
    volume_m3: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _col, taxon in EGG_CATEGORIES:
        if taxon not in sampled_counts:
            continue
        count = sampled_counts[taxon]
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


def _quantile(sorted_vals: list[float], p: float) -> float | None:
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    rank = (p / 100.0) * (len(sorted_vals) - 1)
    lo = int(math.floor(rank))
    hi = int(math.ceil(rank))
    if lo == hi:
        return sorted_vals[lo]
    weight = rank - lo
    return sorted_vals[lo] * (1 - weight) + sorted_vals[hi] * weight


def _speed_quantile_report(speeds: list[float]) -> dict[str, float | None]:
    if not speeds:
        return {k: None for k in ("min", "p5", "p25", "p50", "p75", "p95", "max")}
    ordered = sorted(speeds)
    return {
        "min": ordered[0],
        "p5": _quantile(ordered, 5),
        "p25": _quantile(ordered, 25),
        "p50": _quantile(ordered, 50),
        "p75": _quantile(ordered, 75),
        "p95": _quantile(ordered, 95),
        "max": ordered[-1],
    }


def _empty_qc_report() -> dict[str, Any]:
    return {
        "events_read": 0,
        "dropped_by_rule": {label: 0 for label, _ in QC_RULE_LABELS},
        "units_rows_skipped": 0,
        "pump_qc_detail": {
            "pump_missing": 0,
            "pump_out_of_bounds": 0,
            "pump_ratio": 0,
            "pump_invalid_unique_events": 0,
        },
        "egg_cell_qc": EGG_CELL_QC_DOCUMENTATION,
        "dropped_rows": 0,
        "dropped_unique_total": 0,
        "events_kept": 0,
        "events_kept_duration_2_to_10_min": 0,
        "single_pump_reading_event_ids": [],
        "implied_speed_knots_quantiles": {
            "duration_under_10_min": _speed_quantile_report([]),
            "duration_10_min_or_more": _speed_quantile_report([]),
            "speed_review_flag_count": 0,
        },
        "cruise_taxon_qc": [],
        "cruise_taxon_review_flags": [],
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
class _CruiseTaxonAccumulator:
    sampled_counts: list[int] = field(default_factory=list)
    not_sampled_events: int = 0


def _finalize_cruise_taxon_qc(
    accum: dict[tuple[str, str], _CruiseTaxonAccumulator],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    table: list[dict[str, Any]] = []
    taxon_all_zero_cruises: dict[str, list[str]] = {}
    taxon_nan_cruises: dict[str, set[str]] = {}

    for (cruise, taxon), stats in sorted(accum.items()):
        events_sampled = len(stats.sampled_counts)
        all_zero = events_sampled > 0 and all(c == 0 for c in stats.sampled_counts)
        row = {
            "cruise": cruise,
            "taxon": taxon,
            "events_sampled": events_sampled,
            "events_not_sampled": stats.not_sampled_events,
            "all_counts_zero": all_zero,
        }
        table.append(row)
        if stats.not_sampled_events > 0:
            taxon_nan_cruises.setdefault(taxon, set()).add(cruise)
        if all_zero:
            taxon_all_zero_cruises.setdefault(taxon, []).append(cruise)

    flags: list[dict[str, str]] = []
    for taxon, zero_cruises in taxon_all_zero_cruises.items():
        nan_cruises = taxon_nan_cruises.get(taxon, set())
        for cruise in sorted(zero_cruises):
            if nan_cruises - {cruise}:
                flags.append(
                    {
                        "cruise": cruise,
                        "taxon": taxon,
                        "reason": "all_zero_on_cruise_while_not_sampled_on_other_cruises",
                    }
                )
    return table, flags


@dataclass
class TransformResult:
    events: list[dict[str, Any]] = field(default_factory=list)
    counts: list[dict[str, Any]] = field(default_factory=list)
    qc_report: dict[str, Any] = field(default_factory=_empty_qc_report)


def transform_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    max_duration_min: float = DEFAULT_MAX_DURATION_MIN,
    units_rows_skipped: int = 0,
) -> TransformResult:
    """
    Build events and counts only for rows that pass all QC rules.

    Failed events are omitted from events, counts (including explicit zeros), and DwC.
    """
    result = TransformResult()
    report = result.qc_report
    report["units_rows_skipped"] = units_rows_skipped
    dropped_event_ids: set[str] = set()
    pump_dropped_event_ids: set[str] = set()
    dropped_rows = 0
    kept_ids: set[str] = set()
    seen_event_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    cruise_taxon: dict[tuple[str, str], _CruiseTaxonAccumulator] = {}
    speeds_under_10: list[float] = []
    speeds_10_or_more: list[float] = []
    speed_review_count = 0
    kept_2_to_10 = 0
    single_pump_ids: list[str] = []

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
            max_duration_min=max_duration_min,
            pump_qc_detail=report["pump_qc_detail"],
        )
        if flags != 0:
            _record_drop(flags, report["dropped_by_rule"])
            dropped_rows += 1
            if not keys_invalid(row):
                dropped_event_ids.add(event_id)
                if flags & QC_PUMP_INVALID:
                    pump_dropped_event_ids.add(event_id)
            continue

        vol, pump_used = volume_m3_for_row(row)
        if vol is None or vol <= 0:
            report["dropped_by_rule"]["invalid_volume"] += 1
            dropped_rows += 1
            dropped_event_ids.add(event_id)
            continue

        _, sampled_counts = egg_qc_flags(row)
        if sampled_counts is None:
            raise ValueError("internal: sampled counts missing after QC pass")

        start_t = _parse_erddap_time(row.get("time"))
        stop_t = _parse_erddap_time(row.get("stop_time"))
        _, duration_min = duration_qc_flags(start_t, stop_t, max_duration_min=max_duration_min)
        if duration_min is None:
            raise ValueError(f"internal: duration missing after QC pass: {event_id}")

        event = row_to_event(row, float(vol), pump_used, duration_min)
        kept_ids.add(event_id)
        result.events.append(event)
        result.counts.extend(row_to_occurrences(sampled_counts, event_id, float(vol)))

        if pump_used == 1:
            single_pump_ids.append(event_id)

        if MIN_DURATION_BOTH_SECONDS_NONZERO_MIN <= duration_min < SHORT_EVENT_THRESHOLD_MIN:
            kept_2_to_10 += 1

        speed = event.get("implied_speed_kn")
        if speed is not None:
            if duration_min < SHORT_EVENT_THRESHOLD_MIN:
                speeds_under_10.append(float(speed))
            else:
                speeds_10_or_more.append(float(speed))
        if event.get("speed_review_flag"):
            speed_review_count += 1

        egg_state = classify_egg_row(row)
        for _col, taxon in EGG_CATEGORIES:
            key = (cruise, taxon)
            acc = cruise_taxon.setdefault(key, _CruiseTaxonAccumulator())
            if taxon in egg_state.sampled:
                acc.sampled_counts.append(egg_state.sampled[taxon])
            else:
                acc.not_sampled_events += 1

    if duplicate_ids:
        ordered = ", ".join(sorted(duplicate_ids))
        raise ValueError(f"duplicate event_id(s): {ordered}")

    report["dropped_rows"] = dropped_rows
    report["dropped_unique_total"] = len(dropped_event_ids)
    report["pump_qc_detail"]["pump_invalid_unique_events"] = len(pump_dropped_event_ids)
    report["events_kept"] = len(kept_ids)
    report["events_kept_duration_2_to_10_min"] = kept_2_to_10
    report["single_pump_reading_event_ids"] = sorted(single_pump_ids)
    report["implied_speed_knots_quantiles"] = {
        "duration_under_10_min": _speed_quantile_report(speeds_under_10),
        "duration_10_min_or_more": _speed_quantile_report(speeds_10_or_more),
        "speed_review_flag_count": speed_review_count,
    }
    cruise_table, review_flags = _finalize_cruise_taxon_qc(cruise_taxon)
    report["cruise_taxon_qc"] = cruise_table
    report["cruise_taxon_review_flags"] = review_flags
    _validate_qc_report(report)
    return result
