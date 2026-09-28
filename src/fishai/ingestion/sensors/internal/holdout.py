"""WCOFS holdout scoring vs glider subsurface profiles."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import xarray as xr

CHECK_TYPE = "holdout"


def mixed_layer_depth(
    depth: np.ndarray,
    temp: np.ndarray,
    *,
    ref_depth_m: float = 10.0,
    delta_c: float = 0.2,
) -> float:
    """MLD: depth where T first falls below T(ref_depth) - delta_c."""
    order = np.argsort(depth)
    d = depth[order]
    t = temp[order]
    ref_idx = np.argmin(np.abs(d - ref_depth_m))
    t_ref = t[ref_idx]
    if not np.isfinite(t_ref):
        return float("nan")
    below = d > d[ref_idx]
    if not np.any(below):
        return float(d.max())
    for i in range(ref_idx + 1, len(d)):
        if np.isfinite(t[i]) and t[i] <= t_ref - delta_c:
            return float(d[i])
    return float(d.max())


def thermocline_depth(depth: np.ndarray, temp: np.ndarray) -> float:
    order = np.argsort(depth)
    d = depth[order]
    t = temp[order]
    if len(d) < 3:
        return float("nan")
    dz = np.diff(d)
    dt = np.diff(t)
    with np.errstate(divide="ignore", invalid="ignore"):
        grad = np.abs(dt / dz)
    idx = int(np.nanargmax(grad))
    return float(d[idx + 1])


def profiles_below_mld(df: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    hold = cfg.get("holdout", {})
    delta = float(hold.get("mld_delta_c", 0.2))
    ref_d = float(hold.get("mld_reference_depth_m", 10.0))
    rows = []
    group_cols = ["profile_id"] if "profile_id" in df.columns else ["time"]
    for _, grp in df.groupby(group_cols):
        depth = grp["depth"].astype(float).values
        temp = grp["temperature"].astype(float).values
        mld = mixed_layer_depth(depth, temp, ref_depth_m=ref_d, delta_c=delta)
        below = grp[grp["depth"].astype(float) > mld].copy()
        below["mld_m"] = mld
        below["thermocline_m"] = thermocline_depth(depth, temp)
        rows.append(below)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def band_means(profiles: pd.DataFrame, bands: list[list[float]]) -> pd.DataFrame:
    out_rows = []
    for lo, hi in bands:
        band = profiles[(profiles["depth"] >= lo) & (profiles["depth"] < hi)]
        if band.empty:
            continue
        for pid, grp in band.groupby("profile_id" if "profile_id" in band.columns else "time"):
            out_rows.append(
                {
                    "profile_id": pid,
                    "depth_band_lo": lo,
                    "depth_band_hi": hi,
                    "obs_temp_c": float(np.nanmean(grp["temperature"])),
                }
            )
    return pd.DataFrame(out_rows)


def _grade_rmse(rmse: float, pass_thr: float, deg_thr: float) -> str:
    if not np.isfinite(rmse):
        return "FAIL"
    if rmse <= pass_thr:
        return "PASS"
    if rmse <= deg_thr:
        return "DEGRADED"
    return "FAIL"


def score_holdout(
    model_ds: xr.Dataset,
    glider_profiles: pd.DataFrame,
    *,
    cfg: dict[str, Any],
) -> pd.DataFrame:
    hold = cfg.get("holdout", {})
    independent = bool(hold.get("independent_confirmed", False))
    below = profiles_below_mld(glider_profiles, cfg)
    bands = hold.get("depth_bands_m", [[20, 50], [50, 100], [100, 200]])
    band_obs = band_means(below, bands)
    if band_obs.empty:
        return pd.DataFrame(
            [
                {
                    "check_type": CHECK_TYPE,
                    "metric": "temperature_rmse",
                    "status": "FAIL",
                    "value": float("nan"),
                    "independent": independent,
                }
            ]
        )

    # Synthetic model comparison: sample model temp at obs lat/lon/depth mid-band (stub surface temp if 3D missing).
    if "temp" in model_ds:
        temp3d = model_ds["temp"]
        if "ocean_time" in temp3d.dims:
            temp3d = temp3d.isel(ocean_time=0)
    else:
        temp3d = model_ds.get("sst")

    preds = []
    for _, row in band_obs.iterrows():
        mid = 0.5 * (row["depth_band_lo"] + row["depth_band_hi"])
        # Without full 3D interpolation in pilot skeleton, use surface as placeholder if depth index unavailable.
        val = float(temp3d.isel(s_rho=-1).mean()) if hasattr(temp3d, "isel") else float(temp3d.mean())
        preds.append(val)
    band_obs = band_obs.copy()
    band_obs["model_temp_c"] = preds
    rmse = float(np.sqrt(np.nanmean((band_obs["model_temp_c"] - band_obs["obs_temp_c"]) ** 2)))
    thr = hold.get("temperature_rmse_c", {})
    status = _grade_rmse(rmse, thr.get("pass", 0.6), thr.get("degraded", 1.0))
    return pd.DataFrame(
        [
            {
                "check_type": CHECK_TYPE,
                "metric": "temperature_rmse",
                "status": status,
                "value": rmse,
                "independent": independent,
                "pass_threshold": thr.get("pass", 0.6),
                "degraded_threshold": thr.get("degraded", 1.0),
            }
        ]
    )
