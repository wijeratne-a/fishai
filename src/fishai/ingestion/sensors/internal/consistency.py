"""WCOFS vs HF radar / NDBC consistency scoring on the 10 km training grid only."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import xarray as xr

from fishai.ingestion.sensors.internal.grid import (
    aggregate_hfr_to_grid,
    aggregate_ndbc_sst_to_grid,
    build_training_grid_10km,
    model_on_training_grid,
)

CHECK_TYPE = "consistency"
GRID_MODE = "grid_10km"


def _complex_vector_correlation(u_m: np.ndarray, v_m: np.ndarray, u_o: np.ndarray, v_o: np.ndarray) -> float:
    cm = (u_m + 1j * v_m).ravel()
    co = (u_o + 1j * v_o).ravel()
    mask = np.isfinite(cm.real) & np.isfinite(co.real)
    if mask.sum() < 3:
        return float("nan")
    cm = cm[mask]
    co = co[mask]
    num = np.abs(np.sum(cm * np.conjugate(co)))
    den = np.sqrt(np.sum(np.abs(cm) ** 2) * np.sum(np.abs(co) ** 2))
    if den == 0:
        return float("nan")
    return float(num / den)


def _rmse(a: np.ndarray, b: np.ndarray) -> float:
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() == 0:
        return float("nan")
    return float(np.sqrt(np.mean((a[mask] - b[mask]) ** 2)))


def _bias(a: np.ndarray, b: np.ndarray) -> float:
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(a[mask] - b[mask]))


def _grade(value: float, pass_thr: float, degraded_thr: float, higher_is_better: bool) -> str:
    if not np.isfinite(value):
        return "FAIL"
    if higher_is_better:
        if value >= pass_thr:
            return "PASS"
        if value >= degraded_thr:
            return "DEGRADED"
        return "FAIL"
    if value <= pass_thr:
        return "PASS"
    if value <= degraded_thr:
        return "DEGRADED"
    return "FAIL"


def _align_model_surface(model_ds: xr.Dataset) -> xr.Dataset:
    """Normalize WCOFS-like fields to lat/lon grid with sst and optional u_east, v_north."""
    if "sst" not in model_ds:
        if "T3m" in model_ds:
            sst = model_ds["T3m"]
        elif "temp" in model_ds:
            sst = model_ds["temp"]
            if "s_rho" in sst.dims:
                sst = sst.isel(s_rho=-1)
        else:
            raise KeyError("model_ds must include temp, T3m, or sst")
        for dim in ("lead_hours", "ocean_time"):
            if dim in sst.dims:
                sst = sst.isel({dim: 0})
        model_ds = model_ds.assign(sst=sst.squeeze())
    if "u_east" in model_ds and "v_north" in model_ds:
        ue = model_ds["u_east"]
        vn = model_ds["v_north"]
        if "s_rho" in ue.dims:
            ue = ue.isel(s_rho=-1)
            vn = vn.isel(s_rho=-1)
        for dim in ("lead_hours", "ocean_time"):
            if dim in ue.dims:
                ue = ue.isel({dim: 0})
                vn = vn.isel({dim: 0})
        model_ds = model_ds.assign(u_east=ue.squeeze(), v_north=vn.squeeze())
    return model_ds


def score_cycle(
    model_ds: xr.Dataset,
    obs: dict[str, Any],
    *,
    cfg: dict[str, Any],
    training_grid: xr.Dataset | None = None,
) -> pd.DataFrame:
    """Compare WCOFS to instruments on the 10 km grid (no species predictions at points)."""
    model_ds = _align_model_surface(model_ds)
    grid = training_grid or build_training_grid_10km(cfg)
    model_grid = model_on_training_grid(model_ds, grid)
    thresholds = cfg.get("consistency", {})
    rows: list[dict[str, Any]] = []

    def add_row(metric: str, value: float, variable: str, pass_thr: float, deg_thr: float, higher: bool):
        rows.append(
            {
                "check_type": CHECK_TYPE,
                "metric": metric,
                "variable": variable,
                "grid_mode": GRID_MODE,
                "value": value,
                "pass_threshold": pass_thr,
                "degraded_threshold": deg_thr,
                "status": _grade(value, pass_thr, deg_thr, higher),
            }
        )

    hfr = obs.get("hfr")
    if hfr is not None and len(hfr.time) > 0:
        hf_grid = aggregate_hfr_to_grid(hfr, grid)
        corr = _complex_vector_correlation(
            model_grid["u_east"].values,
            model_grid["v_north"].values,
            hf_grid["water_u"].values,
            hf_grid["water_v"].values,
        )
        rmse = _rmse(
            np.hypot(model_grid["u_east"].values, model_grid["v_north"].values),
            np.hypot(hf_grid["water_u"].values, hf_grid["water_v"].values),
        )
        t = thresholds.get("current_vector_corr", {})
        add_row("vector_corr", corr, "current", t.get("pass", 0.65), t.get("degraded", 0.45), True)
        t = thresholds.get("current_rmse_ms", {})
        add_row("rmse", rmse, "current", t.get("pass", 0.18), t.get("degraded", 0.30), False)

    ndbc = obs.get("ndbc")
    if ndbc is not None and not ndbc.empty and "WTMP" in ndbc.columns:
        sst_grid = aggregate_ndbc_sst_to_grid(ndbc, grid)
        bias = _bias(model_grid["sst"].values, sst_grid["sst_obs"].values)
        rmse = _rmse(model_grid["sst"].values, sst_grid["sst_obs"].values)
        t = thresholds.get("sst_bias_c", {})
        add_row("bias", abs(bias), "sst", t.get("pass", 0.75), t.get("degraded", 1.25), False)
        t = thresholds.get("sst_rmse_c", {})
        add_row("rmse", rmse, "sst", t.get("pass", 0.90), t.get("degraded", 1.40), False)

    return pd.DataFrame(rows)
