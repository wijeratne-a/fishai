"""Operational lag covariates: GLORYS fields at event track, N days before event mid-time."""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np
import pandas as pd

from fishai.ingestion.physics.covariates import (
    COL_EVENT_ID,
    CUFES_COVARIATE_FIELDS,
    DEFAULT_GRID_CELL_KM,
    event_mid_time,
    mean_covariates_along_segment,
    normalize_cufes_events_for_physics,
)
from fishai.ingestion.physics.cufes_training_covariates import GlorysFieldStore

# Fields requested for jack mackerel lag experiment (SST proxy, gradient, MLD).
LAGGED_PHYSICS_FIELDS: tuple[str, ...] = ("T3m", "sst_grad", "MLD_m")

DEFAULT_LAG_DAYS: tuple[int, ...] = (7, 14)


def lagged_column_name(field: str, lag_days: int) -> str:
    return f"{field}_lag{lag_days}d"


def unique_event_days_with_lags(
    events: pd.DataFrame,
    *,
    lag_days: Sequence[int] = DEFAULT_LAG_DAYS,
) -> list[dt.date]:
    """Calendar days needed for instantaneous joins plus each operational lag."""
    from fishai.ingestion.physics.cufes_training_covariates import unique_event_days

    days: set[dt.date] = set(unique_event_days(events))
    events = normalize_cufes_events_for_physics(events)
    for _, row in events.iterrows():
        mid = event_mid_time(row)
        if pd.isna(mid):
            continue
        for lag in lag_days:
            days.add((mid - pd.Timedelta(days=int(lag))).date())
    return sorted(days)


def _shifted_sampler(store: GlorysFieldStore, lag_days: int):
    def sampler(lat: float, lon: float, when: pd.Timestamp) -> dict[str, Any]:
        if pd.isna(when):
            return {f: float("nan") for f in CUFES_COVARIATE_FIELDS}
        shifted = when - pd.Timedelta(days=int(lag_days))
        return store.field_sampler(lat, lon, shifted)

    return sampler


def sample_lagged_physics_for_event(
    event: pd.Series,
    store: GlorysFieldStore,
    *,
    lag_days: Sequence[int] = DEFAULT_LAG_DAYS,
    fields: Sequence[str] = LAGGED_PHYSICS_FIELDS,
    grid_cell_km: float = DEFAULT_GRID_CELL_KM,
) -> dict[str, float]:
    """Segment-mean covariates at each lag (same geometry as instantaneous join)."""
    out: dict[str, float] = {}
    for lag in lag_days:
        sampled, _reasons = mean_covariates_along_segment(
            event,
            _shifted_sampler(store, lag),
            grid_cell_km=grid_cell_km,
        )
        for field in fields:
            col = lagged_column_name(field, int(lag))
            val = sampled.get(field, np.nan)
            out[col] = float(val) if val is not None else float("nan")
    return out


def attach_lagged_physics_columns(
    events: pd.DataFrame,
    store: GlorysFieldStore,
    *,
    lag_days: Sequence[int] = DEFAULT_LAG_DAYS,
    fields: Sequence[str] = LAGGED_PHYSICS_FIELDS,
) -> pd.DataFrame:
    """One row per ``event_id`` with lag columns (does not alter exclusion flags)."""
    events = normalize_cufes_events_for_physics(events)
    rows: list[dict[str, Any]] = []
    for _, event in events.iterrows():
        eid = event[COL_EVENT_ID]
        lag_vals = sample_lagged_physics_for_event(
            event, store, lag_days=lag_days, fields=fields
        )
        rows.append({COL_EVENT_ID: eid, **lag_vals})
    return pd.DataFrame(rows)


def required_lagged_columns(
    lag_days: Iterable[int] = DEFAULT_LAG_DAYS,
    fields: Iterable[str] = LAGGED_PHYSICS_FIELDS,
) -> list[str]:
    return [lagged_column_name(f, int(lag)) for lag in lag_days for f in fields]


def rows_with_complete_lags(df: pd.DataFrame, lag_cols: Sequence[str]) -> pd.Series:
    """True for rows where every lag column is finite."""
    if not lag_cols:
        return pd.Series(True, index=df.index)
    ok = pd.Series(True, index=df.index)
    for col in lag_cols:
        if col not in df.columns:
            return pd.Series(False, index=df.index)
        vals = pd.to_numeric(df[col], errors="coerce")
        ok &= np.isfinite(vals.to_numpy(dtype=float))
    return ok
