"""CUFES event covariate contract and join to bot1 ``cufes_events`` tables."""

from __future__ import annotations

import json
import math
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# bot1 ``cufes_events.parquet`` column names (PR #4 / feature/bio-cufes-ingest).
COL_EVENT_ID = "event_id"
COL_START_TIME = "start_time"
COL_STOP_TIME = "stop_time"
COL_START_LAT = "start_latitude"
COL_START_LON = "start_longitude"
COL_STOP_LAT = "stop_latitude"
COL_STOP_LON = "stop_longitude"

REQUIRED_EVENT_COLUMNS: tuple[str, ...] = (
    COL_EVENT_ID,
    COL_START_TIME,
    COL_STOP_TIME,
    COL_START_LAT,
    COL_START_LON,
    COL_STOP_LAT,
    COL_STOP_LON,
)

# Training / hindcast covariates along each CUFES tow segment (egg-stage model).
CUFES_COVARIATE_FIELDS: tuple[str, ...] = (
    "T3m",
    "S3m",
    "MLD_m",
    "sst_grad",
    "front_distance_km",
    "upwelling",
)

FEATURE_STORE_EXTRA_FIELDS: tuple[str, ...] = (
    "bottomT",
    "mlotst_crosscheck",
)

MLD_COVARIATE_SOURCE = "computed_temperature_threshold"
MLDST_FIELD_ROLE = "cross_check_only"

from fishai.ingestion.physics.geo_distance import haversine_km  # noqa: E402

DEFAULT_GRID_CELL_KM = 4.0
MIN_TRACK_LENGTH_KM = 1e-6

DROP_REASON_LAND_MASK = "land_mask"
DROP_REASON_MISSING_COVARIATE = "missing_covariate"
DROP_REASON_TOO_FEW_TRACK_POINTS = "too_few_track_points"
DROP_REASON_MISSING_ENDPOINT = "missing_endpoint"

DROP_REASONS_ALL: tuple[str, ...] = (
    DROP_REASON_LAND_MASK,
    DROP_REASON_MISSING_COVARIATE,
    DROP_REASON_TOO_FEW_TRACK_POINTS,
    DROP_REASON_MISSING_ENDPOINT,
)

DROP_SUMMARY_JSON_SCHEMA_VERSION = 1
DEFAULT_COVARIATE_DROPS_PARQUET_NAME = "cufes_physics_covariate_drops.parquet"
DEFAULT_COVARIATE_DROP_SUMMARY_JSON_NAME = "cufes_physics_covariate_drop_summary.json"

DROP_TABLE_COLUMNS: tuple[str, ...] = (
    "event_id",
    "reason",
    "covariate",
    "latitude",
    "longitude",
)

# Optional per-sample flag from ``field_sampler`` (not a model covariate).
SAMPLER_LAND_MASK_KEY = "land_mask"


class CufesEventValidationError(ValueError):
    """Invalid ``cufes_events`` input for physics covariate join."""


def validate_cufes_events(events: pd.DataFrame) -> None:
    """Require unique, non-null ``event_id`` and bot1 segment columns."""
    missing_cols = [c for c in REQUIRED_EVENT_COLUMNS if c not in events.columns]
    if missing_cols:
        raise CufesEventValidationError(f"missing columns: {missing_cols}")
    if events[COL_EVENT_ID].isna().any():
        raise CufesEventValidationError("event_id must not be null")
    if events[COL_EVENT_ID].astype(str).str.strip().eq("").any():
        raise CufesEventValidationError("event_id must not be empty")
    if events[COL_EVENT_ID].duplicated().any():
        dupes = events.loc[events[COL_EVENT_ID].duplicated(), COL_EVENT_ID].tolist()
        raise CufesEventValidationError(f"duplicate event_id values: {dupes[:5]}")


def event_midpoint_lat_lon(event: pd.Series) -> tuple[float, float]:
    if not endpoints_present(event):
        return float("nan"), float("nan")
    lat = (float(event[COL_START_LAT]) + float(event[COL_STOP_LAT])) / 2.0
    lon = (float(event[COL_START_LON]) + float(event[COL_STOP_LON])) / 2.0
    return lat, lon


def _gc_point(lat1: float, lon1: float, lat2: float, lon2: float, frac: float) -> tuple[float, float]:
    """Intermediate point on the great-circle path (frac in [0, 1])."""
    if frac <= 0.0:
        return lat1, lon1
    if frac >= 1.0:
        return lat2, lon2
    phi1, lam1, phi2, lam2 = map(math.radians, (lat1, lon1, lat2, lon2))
    sin_d = math.sqrt(
        (math.sin((phi2 - phi1) / 2) ** 2)
        + math.cos(phi1) * math.cos(phi2) * math.sin((lam2 - lam1) / 2) ** 2
    )
    d = 2 * math.asin(min(1.0, sin_d))
    if d == 0.0:
        return lat1, lon1
    a = math.sin((1 - frac) * d) / math.sin(d)
    b = math.sin(frac * d) / math.sin(d)
    x = a * math.cos(phi1) * math.cos(lam1) + b * math.cos(phi2) * math.cos(lam2)
    y = a * math.cos(phi1) * math.sin(lam1) + b * math.cos(phi2) * math.sin(lam2)
    z = a * math.sin(phi1) + b * math.sin(phi2)
    lat = math.degrees(math.atan2(z, math.sqrt(x * x + y * y)))
    lon = math.degrees(math.atan2(y, x))
    return lat, lon


def great_circle_sample_points(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    *,
    grid_cell_km: float = DEFAULT_GRID_CELL_KM,
) -> list[tuple[float, float]]:
    """
    Sample points along the great-circle segment (start → stop).

    Uses at least start, midpoint, and stop, and adds ~one point per model grid
    cell crossed along the track.
    """
    dist_km = haversine_km(lat1, lon1, lat2, lon2)
    n_pts = max(3, int(math.ceil(dist_km / grid_cell_km)) + 1)
    fracs = np.linspace(0.0, 1.0, n_pts)
    return [_gc_point(lat1, lon1, lat2, lon2, float(f)) for f in fracs]


def event_mid_time(event: pd.Series) -> pd.Timestamp:
    start = pd.to_datetime(event[COL_START_TIME], utc=True, errors="coerce")
    stop = pd.to_datetime(event[COL_STOP_TIME], utc=True, errors="coerce")
    if pd.isna(start) or pd.isna(stop):
        return pd.NaT
    return start + (stop - start) / 2


def endpoints_present(event: pd.Series) -> bool:
    for col in (COL_START_LAT, COL_START_LON, COL_STOP_LAT, COL_STOP_LON):
        val = event[col]
        if val is None or (isinstance(val, float) and math.isnan(val)) or pd.isna(val):
            return False
    return True


def mean_covariates_along_segment(
    event: pd.Series,
    field_sampler: Callable[[float, float, pd.Timestamp], dict[str, Any]],
    *,
    grid_cell_km: float = DEFAULT_GRID_CELL_KM,
) -> tuple[dict[str, float], list[str]]:
    """
    Mean of gridded covariates along the tow segment at mid-time.

    Returns covariate values and segment-level drop reason codes (may be empty).
    """
    if not endpoints_present(event):
        return {field: float("nan") for field in CUFES_COVARIATE_FIELDS}, []
    lat0, lon0 = float(event[COL_START_LAT]), float(event[COL_START_LON])
    lat1, lon1 = float(event[COL_STOP_LAT]), float(event[COL_STOP_LON])
    segment_reasons: list[str] = []
    dist_km = haversine_km(lat0, lon0, lat1, lon1)
    if dist_km < MIN_TRACK_LENGTH_KM:
        segment_reasons.append(DROP_REASON_TOO_FEW_TRACK_POINTS)
    mid_t = event_mid_time(event)
    points = great_circle_sample_points(lat0, lon0, lat1, lon1, grid_cell_km=grid_cell_km)
    if len(points) < 3:
        segment_reasons.append(DROP_REASON_TOO_FEW_TRACK_POINTS)
    stacks: dict[str, list[float]] = {f: [] for f in CUFES_COVARIATE_FIELDS}
    for lat, lon in points:
        sampled = field_sampler(lat, lon, mid_t)
        if sampled.get(SAMPLER_LAND_MASK_KEY) is True:
            if DROP_REASON_LAND_MASK not in segment_reasons:
                segment_reasons.append(DROP_REASON_LAND_MASK)
        for field in CUFES_COVARIATE_FIELDS:
            val = sampled.get(field, np.nan)
            stacks[field].append(float(val) if val is not None else float("nan"))
    out: dict[str, float] = {}
    for field, vals in stacks.items():
        arr = np.asarray(vals, dtype=float)
        out[field] = float(np.nanmean(arr)) if np.isfinite(arr).any() else float("nan")
    return out, segment_reasons


def missing_covariate_counts(covariates: pd.DataFrame) -> dict[str, int]:
    counts: dict[str, int] = {}
    for col in CUFES_COVARIATE_FIELDS:
        if col in covariates.columns:
            counts[col] = int(covariates[col].isna().sum())
    return counts


def _drop_qc_counts(
    drops: pd.DataFrame,
) -> tuple[dict[str, int], dict[str, int], int]:
    """Unique events per reason, drop-table row counts per reason, unique events dropped."""
    if drops.empty:
        return {}, {}, 0
    rows_by_reason = drops.groupby("reason").size().astype(int).to_dict()
    drop_summary = drops.groupby("reason")["event_id"].nunique().astype(int).to_dict()
    dropped_unique_total = int(drops["event_id"].nunique())
    return drop_summary, rows_by_reason, dropped_unique_total


def write_covariate_drop_table(drops: pd.DataFrame, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    drops.to_parquet(path, index=False)
    return path


def build_covariate_drop_summary_json(
    drop_summary: dict[str, Any],
    rows_by_reason: dict[str, int],
) -> dict[str, Any]:
    """
    Map in-memory ``qc['drop_summary']`` to the JSON document for R (``jsonlite``).

    Schema (``schema_version`` 1)::

        {
          "schema_version": 1,
          "input_event_count": <int>,
          "dropped_unique_total": <int>,
          "unique_by_reason": {<reason>: <int>, ...},
          "rows_by_reason": {<reason>: <int>, ...}
        }

    Every ``DROP_REASON_*`` appears in both reason maps (0 when unused).
    Default artifact name: ``cufes_physics_covariate_drop_summary.json`` beside
    ``cufes_physics_covariate_drops.parquet``.
    """
    unique_by_reason = {reason: int(drop_summary.get(reason, 0)) for reason in DROP_REASONS_ALL}
    row_counts = {reason: int(rows_by_reason.get(reason, 0)) for reason in DROP_REASONS_ALL}
    return {
        "schema_version": DROP_SUMMARY_JSON_SCHEMA_VERSION,
        "input_event_count": int(drop_summary["input_event_count"]),
        "dropped_unique_total": int(drop_summary["dropped_unique_total"]),
        "unique_by_reason": unique_by_reason,
        "rows_by_reason": row_counts,
    }


def write_covariate_drop_summary(summary: dict[str, Any], path: Path) -> Path:
    """Write UTF-8 JSON with sorted keys and plain ``int`` values (no numpy types)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(summary, sort_keys=True, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
    return path


def join_covariates_to_events(
    events: pd.DataFrame,
    *,
    field_sampler: Callable[[float, float, pd.Timestamp], dict[str, Any]],
    source: str,
    provenance: str = "",
    grid_cell_km: float = DEFAULT_GRID_CELL_KM,
    drops_parquet_path: Path | None = None,
    drop_summary_json_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    """
    One covariate row per input ``event_id``.

    Input must be bot1 ``cufes_events`` rows that already passed biology QC (PR #4
    ``transform_rows`` kept events only), not the raw ERDDAP pull. For the CalCOFI
    pilot that is the QC-kept subset (e.g. 14,592 events), not all rows read from
    ERDDAP (~15,969). Downstream pipelines compare ``drop_summary['input_event_count']``
    to their configured expected kept-event count.

    Covariates are means along the great-circle tow segment (start/stop positions
    from bot1), sampled at mid-time. Rows with any drop-table reason get
    ``excluded=True`` and all model covariates set to NaN; downstream training
    and evaluation must filter ``excluded == False``.

    Duplicate ``event_id`` values raise ``CufesEventValidationError``. Missing
    endpoints → drop reason ``missing_endpoint`` and excluded row.

    ``drop_summary`` reports ``input_event_count``, unique events per ``reason``,
    and ``dropped_unique_total``.

    Optional ``drop_summary_json_path`` writes the flat JSON schema for R
    (``freeze.R`` / ``jsonlite``); see ``build_covariate_drop_summary_json``.
    """
    validate_cufes_events(events)
    input_event_count = int(events[COL_EVENT_ID].nunique())
    if input_event_count != len(events):
        raise CufesEventValidationError(
            "duplicate event_id values: input row count must equal unique event_id count"
        )
    endpoint_missing = 0
    rows: list[dict[str, Any]] = []
    drop_rows: list[dict[str, Any]] = []
    for _, event in events.iterrows():
        mid_lat, mid_lon = event_midpoint_lat_lon(event)
        eid = event[COL_EVENT_ID]
        if not endpoints_present(event):
            endpoint_missing += 1
            sampled = {field: float("nan") for field in CUFES_COVARIATE_FIELDS}
            drop_rows.append(
                {
                    "event_id": eid,
                    "reason": DROP_REASON_MISSING_ENDPOINT,
                    "covariate": None,
                    "latitude": mid_lat,
                    "longitude": mid_lon,
                }
            )
            segment_reasons: list[str] = []
        else:
            sampled, segment_reasons = mean_covariates_along_segment(
                event, field_sampler, grid_cell_km=grid_cell_km
            )
            for reason in segment_reasons:
                drop_rows.append(
                    {
                        "event_id": eid,
                        "reason": reason,
                        "covariate": None,
                        "latitude": mid_lat,
                        "longitude": mid_lon,
                    }
                )
        row: dict[str, Any] = {COL_EVENT_ID: eid}
        for field in CUFES_COVARIATE_FIELDS:
            val = sampled.get(field, np.nan)
            row[field] = np.nan if val is None else val
        row["source"] = source
        row["provenance"] = provenance
        rows.append(row)
        if endpoints_present(event):
            for field in CUFES_COVARIATE_FIELDS:
                if pd.isna(row[field]):
                    drop_rows.append(
                        {
                            "event_id": eid,
                            "reason": DROP_REASON_MISSING_COVARIATE,
                            "covariate": field,
                            "latitude": mid_lat,
                            "longitude": mid_lon,
                        }
                    )
    out = pd.DataFrame(rows)
    drops = pd.DataFrame(drop_rows, columns=list(DROP_TABLE_COLUMNS))
    if len(out) != len(events):
        raise CufesEventValidationError("output row count must equal input event count")
    if out[COL_EVENT_ID].tolist() != events[COL_EVENT_ID].tolist():
        raise CufesEventValidationError("output event_id order must match input")
    if set(out[COL_EVENT_ID]) != set(events[COL_EVENT_ID]):
        raise CufesEventValidationError("output event_id set must equal input")
    reason_counts, rows_by_reason, dropped_unique_total = _drop_qc_counts(drops)
    drop_summary: dict[str, Any] = {
        "input_event_count": input_event_count,
        "dropped_unique_total": dropped_unique_total,
        **reason_counts,
    }
    excluded_ids: set[Any] = set(drops["event_id"].unique()) if not drops.empty else set()
    out["excluded"] = out[COL_EVENT_ID].isin(excluded_ids)
    if excluded_ids:
        for field in CUFES_COVARIATE_FIELDS:
            out.loc[out["excluded"], field] = np.nan
    qc: dict[str, Any] = {
        "missing_by_field": missing_covariate_counts(out),
        "events_endpoint_missing": endpoint_missing,
        "drop_summary": drop_summary,
        "rows_by_reason": rows_by_reason,
        "dropped_unique_total": dropped_unique_total,
    }
    if drops_parquet_path is not None:
        written = write_covariate_drop_table(drops, Path(drops_parquet_path))
        qc["drops_parquet_path"] = str(written)
    if drop_summary_json_path is not None:
        summary_doc = build_covariate_drop_summary_json(drop_summary, rows_by_reason)
        written_json = write_covariate_drop_summary(summary_doc, Path(drop_summary_json_path))
        qc["drop_summary_json_path"] = str(written_json)
    return out, qc, drops
