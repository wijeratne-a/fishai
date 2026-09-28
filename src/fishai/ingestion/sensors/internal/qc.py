"""QARTOD-style QC helpers and bitmask flags."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr

# Bitmask flags (per-value or per-cell).
QC_GOOD = 0
QC_RANGE = 1 << 0
QC_SPIKE = 1 << 1
QC_FLAT = 1 << 2
QC_STALE = 1 << 3
QC_RADAR_HDOP = 1 << 4
QC_RADAR_SITES = 1 << 5


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def apply_range_test(series: pd.Series, lo: float, hi: float) -> pd.Series:
    flags = pd.Series(0, index=series.index, dtype="int64")
    bad = series.notna() & ((series < lo) | (series > hi))
    flags.loc[bad] |= QC_RANGE
    return flags


def apply_spike_test(series: pd.Series, window: int, n_sigma: float) -> pd.Series:
    flags = pd.Series(0, index=series.index, dtype="int64")
    if len(series) < window + 1:
        return flags
    diff = series.diff().abs()
    med = diff.rolling(window, center=True, min_periods=1).median()
    mad = (diff - med).abs().rolling(window, center=True, min_periods=1).median()
    thresh = med + n_sigma * (mad + 1e-9)
    spike = series.notna() & (diff > thresh)
    flags.loc[spike] |= QC_SPIKE
    return flags


def apply_flat_line_test(series: pd.Series, min_points: int, epsilon: float) -> pd.Series:
    flags = pd.Series(0, index=series.index, dtype="int64")
    if len(series) < min_points:
        return flags
    vals = series.values
    run = 1
    for i in range(1, len(vals)):
        if np.isfinite(vals[i]) and np.isfinite(vals[i - 1]) and abs(vals[i] - vals[i - 1]) <= epsilon:
            run += 1
        else:
            if run >= min_points:
                flags.iloc[i - run : i] |= QC_FLAT
            run = 1
    if run >= min_points:
        flags.iloc[len(vals) - run :] |= QC_FLAT
    return flags


def staleness_flags(times: pd.Series, max_age_hours: float, fetched_at: datetime | None = None) -> pd.Series:
    fetched_at = fetched_at or _now_utc()
    if times.dt.tz is None:
        times = times.dt.tz_localize("UTC")
    age_h = (fetched_at - times).dt.total_seconds() / 3600.0
    flags = pd.Series(0, index=times.index, dtype="int64")
    flags.loc[age_h > max_age_hours] |= QC_STALE
    return flags


def qc_ndbc(df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    fetched_at = _now_utc()
    out["fetched_at"] = fetched_at
    qc = pd.Series(0, index=out.index, dtype="int64")
    ranges = cfg.get("range", {})
    if "WTMP" in out.columns and "wtmp_c" in ranges:
        lo, hi = ranges["wtmp_c"]
        qc |= apply_range_test(out["WTMP"], lo, hi)
    for col in ("WTMP",):
        if col in out.columns:
            qc |= apply_spike_test(out[col], cfg.get("spike_window", 3), cfg.get("spike_threshold_sigma", 4.0))
            qc |= apply_flat_line_test(
                out[col],
                cfg.get("flat_line_min_points", 6),
                cfg.get("flat_line_epsilon", 1e-4),
            )
    if "time" in out.columns:
        qc |= staleness_flags(out["time"], cfg.get("staleness_hours", {}).get("ndbc", 6), fetched_at)
    out["qc_flags"] = qc
    return out


def qc_hfradar(ds: xr.Dataset, cfg: dict[str, Any]) -> xr.Dataset:
    fetched_at = np.datetime64(_now_utc().replace(tzinfo=None))
    out = ds.copy()
    out.attrs["fetched_at"] = str(fetched_at)
    hdop_max = float(cfg.get("radar_hdop_max", 1.25))
    min_sites = int(cfg.get("radar_min_sites", 2))
    mask_hdop = (out["hdop"] > hdop_max).values
    mask_sites = (out["number_of_sites"] < min_sites).values
    qc_arr = np.zeros(out["water_u"].shape, dtype=np.int16)
    qc_arr[mask_hdop] |= QC_RADAR_HDOP
    qc_arr[mask_sites] |= QC_RADAR_SITES
    u_lo, u_hi = cfg.get("range", {}).get("water_u_ms", (-3.0, 3.0))
    v_lo, v_hi = cfg.get("range", {}).get("water_v_ms", (-3.0, 3.0))
    bad_u = ((out["water_u"] < u_lo) | (out["water_u"] > u_hi)).values
    bad_v = ((out["water_v"] < v_lo) | (out["water_v"] > v_hi)).values
    qc_arr[bad_u] |= QC_RANGE
    qc_arr[bad_v] |= QC_RANGE
    qc = xr.DataArray(qc_arr, coords=out["water_u"].coords, dims=out["water_u"].dims)
    out["qc_flags"] = qc
    out["water_u"] = out["water_u"].where(~(mask_hdop | mask_sites))
    out["water_v"] = out["water_v"].where(~(mask_hdop | mask_sites))
    return out


def qc_glider_profiles(df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    fetched_at = _now_utc()
    out["fetched_at"] = fetched_at
    qc = pd.Series(0, index=out.index, dtype="int64")
    if "temperature" in out.columns:
        lo, hi = cfg.get("range", {}).get("wtmp_c", (-2.0, 35.0))
        qc |= apply_range_test(out["temperature"], lo, hi)
    if "time" in out.columns:
        qc |= staleness_flags(out["time"], cfg.get("staleness_hours", {}).get("glider", 48), fetched_at)
    out["qc_flags"] = qc
    return out
