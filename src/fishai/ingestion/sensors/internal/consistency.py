"""WCOFS vs HF radar / NDBC consistency scoring."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import xarray as xr

CHECK_TYPE = "consistency"


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
    """Normalize WCOFS-like fields to lat/lon grid with temp, u_east, v_north."""
    if "temp" in model_ds:
        sst = model_ds["temp"]
        if "s_rho" in sst.dims:
            sst = sst.isel(s_rho=-1)
        if "ocean_time" in sst.dims:
            sst = sst.isel(ocean_time=0)
        model_ds = model_ds.assign(sst=sst.squeeze())
    elif "sst" not in model_ds:
        raise KeyError("model_ds must include temp or sst")
    if "u_east" in model_ds and "v_north" in model_ds:
        ue = model_ds["u_east"]
        vn = model_ds["v_north"]
        if "s_rho" in ue.dims:
            ue = ue.isel(s_rho=-1)
            vn = vn.isel(s_rho=-1)
        if "ocean_time" in ue.dims:
            ue = ue.isel(ocean_time=0)
            vn = vn.isel(ocean_time=0)
        model_ds = model_ds.assign(u_east=ue.squeeze(), v_north=vn.squeeze())
    return model_ds


def _hfr_hour_mean(hfr: xr.Dataset, time_idx: int = -1) -> xr.Dataset:
    ds = hfr.isel(time=time_idx)
    return ds


def _nearest_curvilinear(
    model_ds: xr.Dataset,
    lat_pts: np.ndarray,
    lon_pts: np.ndarray,
    var: str,
) -> np.ndarray:
    lat_g = model_ds["lat_rho"].values
    lon_g = model_ds["lon_rho"].values
    field = model_ds[var].values
    out = np.full(lat_pts.shape, np.nan, dtype=float)
    for i, (la, lo) in enumerate(zip(lat_pts.ravel(), lon_pts.ravel(), strict=True)):
        dist = (lat_g - la) ** 2 + (lon_g - lo) ** 2
        ei, xi = np.unravel_index(np.nanargmin(dist), dist.shape)
        out.ravel()[i] = float(field[ei, xi])
    return out


def _regrid_to_training(model: xr.Dataset, training_grid: xr.Dataset) -> xr.Dataset:
    lat = training_grid["lat"] if "lat" in training_grid else training_grid["latitude"]
    lon = training_grid["lon"] if "lon" in training_grid else training_grid["longitude"]
    out = xr.Dataset()
    for var in ("sst", "u_east", "v_north"):
        if var not in model:
            continue
        src = model[var]
        lat_name = "lat_rho" if "lat_rho" in model.coords else "latitude"
        lon_name = "lon_rho" if "lon_rho" in model.coords else "longitude"
        out[var] = src.interp(
            {lat_name: lat, lon_name: lon},
            method="linear",
        )
    return out


def score_cycle(
    model_ds: xr.Dataset,
    obs: dict[str, Any],
    *,
    cfg: dict[str, Any],
    training_grid: xr.Dataset | None = None,
) -> pd.DataFrame:
    """Compare WCOFS surface fields to HF radar and buoy SST.

    ``obs`` keys: ``hfr`` (xr.Dataset), ``ndbc`` (DataFrame with WTMP).
    """
    model_ds = _align_model_surface(model_ds)
    thresholds = cfg.get("consistency", {})
    rows: list[dict[str, Any]] = []

    def add_row(metric: str, value: float, grid_mode: str, variable: str, pass_thr: float, deg_thr: float, higher: bool):
        rows.append(
            {
                "check_type": CHECK_TYPE,
                "metric": metric,
                "variable": variable,
                "grid_mode": grid_mode,
                "value": value,
                "pass_threshold": pass_thr,
                "degraded_threshold": deg_thr,
                "status": _grade(value, pass_thr, deg_thr, higher),
            }
        )

    hfr = obs.get("hfr")
    if hfr is not None and len(hfr.time) > 0:
        hf = _hfr_hour_mean(hfr)
        lat_name = "latitude" if "latitude" in hf.coords else "lat"
        lon_name = "longitude" if "longitude" in hf.coords else "lon"
        # Native: nearest model rho to each HFR cell (sample model at HFR coords).
        lat_pts, lon_pts = np.meshgrid(hf[lat_name].values, hf[lon_name].values, indexing="ij")
        u_mod = _nearest_curvilinear(model_ds, lat_pts, lon_pts, "u_east")
        v_mod = _nearest_curvilinear(model_ds, lat_pts, lon_pts, "v_north")
        u_obs = hf["water_u"].values
        v_obs = hf["water_v"].values
        corr = _complex_vector_correlation(u_mod, v_mod, u_obs, v_obs)
        rmse = _rmse(np.hypot(u_mod, v_mod), np.hypot(u_obs, v_obs))
        t = thresholds.get("current_vector_corr", {})
        add_row("vector_corr", corr, "native", "current", t.get("pass", 0.65), t.get("degraded", 0.45), True)
        t = thresholds.get("current_rmse_ms", {})
        add_row("rmse", rmse, "native", "current", t.get("pass", 0.18), t.get("degraded", 0.30), False)

        if training_grid is not None:
            regridded = _regrid_to_training(model_ds, training_grid)
            # HFR on training grid via interp
            hf_r = hf.interp(
                {lat_name: training_grid["lat"], lon_name: training_grid["lon"]},
                method="nearest",
            )
            corr_r = _complex_vector_correlation(
                regridded["u_east"].values,
                regridded["v_north"].values,
                hf_r["water_u"].values,
                hf_r["water_v"].values,
            )
            rmse_r = _rmse(
                np.hypot(regridded["u_east"].values, regridded["v_north"].values),
                np.hypot(hf_r["water_u"].values, hf_r["water_v"].values),
            )
            t = thresholds.get("current_vector_corr", {})
            add_row("vector_corr", corr_r, "regrid", "current", t.get("pass", 0.65), t.get("degraded", 0.45), True)
            t = thresholds.get("current_rmse_ms", {})
            add_row("rmse", rmse_r, "regrid", "current", t.get("pass", 0.18), t.get("degraded", 0.30), False)

    ndbc = obs.get("ndbc")
    if ndbc is not None and not ndbc.empty and "WTMP" in ndbc.columns:
        preds = _nearest_curvilinear(
            model_ds,
            ndbc["latitude"].astype(float).values,
            ndbc["longitude"].astype(float).values,
            "sst",
        )
        obs_sst = ndbc["WTMP"].astype(float).values
        preds_arr = np.array(preds, dtype=float)
        bias = _bias(preds_arr, obs_sst)
        rmse = _rmse(preds_arr, obs_sst)
        t = thresholds.get("sst_bias_c", {})
        add_row("bias", abs(bias), "native", "sst", t.get("pass", 0.75), t.get("degraded", 1.25), False)
        t = thresholds.get("sst_rmse_c", {})
        add_row("rmse", rmse, "native", "sst", t.get("pass", 0.90), t.get("degraded", 1.40), False)

    return pd.DataFrame(rows)
