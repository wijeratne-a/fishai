"""CUFES event covariate contract and join to bot1 ``cufes_events`` tables."""

from __future__ import annotations

import math
from collections.abc import Callable
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

EARTH_RADIUS_KM = 6371.0
DEFAULT_GRID_CELL_KM = 4.0


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


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    hav = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(hav)))


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
) -> dict[str, float]:
    """Mean of gridded covariates sampled along the tow great-circle segment at mid-time."""
    if not endpoints_present(event):
        return {field: float("nan") for field in CUFES_COVARIATE_FIELDS}
    lat0, lon0 = float(event[COL_START_LAT]), float(event[COL_START_LON])
    lat1, lon1 = float(event[COL_STOP_LAT]), float(event[COL_STOP_LON])
    mid_t = event_mid_time(event)
    points = great_circle_sample_points(lat0, lon0, lat1, lon1, grid_cell_km=grid_cell_km)
    stacks: dict[str, list[float]] = {f: [] for f in CUFES_COVARIATE_FIELDS}
    for lat, lon in points:
        sampled = field_sampler(lat, lon, mid_t)
        for field in CUFES_COVARIATE_FIELDS:
            val = sampled.get(field, np.nan)
            stacks[field].append(float(val) if val is not None else float("nan"))
    out: dict[str, float] = {}
    for field, vals in stacks.items():
        arr = np.asarray(vals, dtype=float)
        out[field] = float(np.nanmean(arr)) if np.isfinite(arr).any() else float("nan")
    return out


def missing_covariate_counts(covariates: pd.DataFrame) -> dict[str, int]:
    counts: dict[str, int] = {}
    for col in CUFES_COVARIATE_FIELDS:
        if col in covariates.columns:
            counts[col] = int(covariates[col].isna().sum())
    return counts


def join_covariates_to_events(
    events: pd.DataFrame,
    *,
    field_sampler: Callable[[float, float, pd.Timestamp], dict[str, Any]],
    source: str,
    provenance: str = "",
    grid_cell_km: float = DEFAULT_GRID_CELL_KM,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    One covariate row per input ``event_id``.

    Covariates are means along the great-circle tow segment (start/stop positions
    from bot1), sampled at mid-time. Missing endpoints → all-NaN covariates.
    """
    validate_cufes_events(events)
    endpoint_missing = 0
    rows: list[dict[str, Any]] = []
    for _, event in events.iterrows():
        if not endpoints_present(event):
            endpoint_missing += 1
            sampled = {field: float("nan") for field in CUFES_COVARIATE_FIELDS}
        else:
            sampled = mean_covariates_along_segment(
                event, field_sampler, grid_cell_km=grid_cell_km
            )
        row: dict[str, Any] = {COL_EVENT_ID: event[COL_EVENT_ID]}
        for field in CUFES_COVARIATE_FIELDS:
            val = sampled.get(field, np.nan)
            row[field] = np.nan if val is None else val
        row["source"] = source
        row["provenance"] = provenance
        rows.append(row)
    out = pd.DataFrame(rows)
    if len(out) != len(events):
        raise CufesEventValidationError("output row count must equal input event count")
    if out[COL_EVENT_ID].tolist() != events[COL_EVENT_ID].tolist():
        raise CufesEventValidationError("output event_id order must match input")
    if set(out[COL_EVENT_ID]) != set(events[COL_EVENT_ID]):
        raise CufesEventValidationError("output event_id set must equal input")
    qc: dict[str, Any] = {
        "missing_by_field": missing_covariate_counts(out),
        "events_endpoint_missing": endpoint_missing,
    }
    return out, qc
