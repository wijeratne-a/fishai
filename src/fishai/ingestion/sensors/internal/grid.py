"""Pilot 10 km training grid for model–instrument comparisons."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import xarray as xr


def training_grid_spacing_km(cfg: dict[str, Any]) -> float:
    return float(cfg.get("training_grid", {}).get("spacing_km", 10.0))


def build_training_grid_10km(cfg: dict[str, Any]) -> xr.Dataset:
    """Regular lat/lon cell centers at ~10 km spacing over the pilot bbox."""
    bbox = cfg["bbox"]
    spacing_km = training_grid_spacing_km(cfg)
    lat_min, lat_max = float(bbox["lat_min"]), float(bbox["lat_max"])
    lon_min, lon_max = float(bbox["lon_min"]), float(bbox["lon_max"])
    lat_c = 0.5 * (lat_min + lat_max)
    dlat = spacing_km / 111.0
    dlon = spacing_km / (111.0 * max(np.cos(np.radians(lat_c)), 1e-6))
    lats = np.arange(lat_min + dlat / 2, lat_max, dlat)
    lons = np.arange(lon_min + dlon / 2, lon_max, dlon)
    return xr.Dataset(coords={"lat": lats, "lon": lons})


def _bin_index(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    idx = np.digitize(values, edges) - 1
    return np.clip(idx, 0, len(edges) - 2)


def aggregate_hfr_to_grid(hfr: xr.Dataset, grid: xr.Dataset) -> xr.Dataset:
    """Mean HF radar vectors on the 10 km grid (no species / prediction fields)."""
    hf = hfr.isel(time=-1)
    lat_name = "latitude" if "latitude" in hf.coords else "lat"
    lon_name = "longitude" if "longitude" in hf.coords else "lon"
    lat_pts = hf[lat_name].values
    lon_pts = hf[lon_name].values
    lat_edges = np.concatenate(
        ([grid["lat"].values[0] - (grid["lat"].values[1] - grid["lat"].values[0]) / 2],
         (grid["lat"].values[:-1] + grid["lat"].values[1:]) / 2,
         [grid["lat"].values[-1] + (grid["lat"].values[-1] - grid["lat"].values[-2]) / 2])
    )
    lon_edges = np.concatenate(
        ([grid["lon"].values[0] - (grid["lon"].values[1] - grid["lon"].values[0]) / 2],
         (grid["lon"].values[:-1] + grid["lon"].values[1:]) / 2,
         [grid["lon"].values[-1] + (grid["lon"].values[-1] - grid["lon"].values[-2]) / 2])
    )
    u_sum = np.zeros((len(grid["lat"]), len(grid["lon"])))
    v_sum = np.zeros_like(u_sum)
    counts = np.zeros_like(u_sum)
    u = hf["water_u"].values
    v = hf["water_v"].values
    for i in range(u.shape[0]):
        for j in range(u.shape[1]):
            la, lo = lat_pts[i], lon_pts[j]
            ui, vi = u[i, j], v[i, j]
            if not (np.isfinite(ui) and np.isfinite(vi)):
                continue
            bi = _bin_index(np.array([la]), lat_edges)[0]
            bj = _bin_index(np.array([lo]), lon_edges)[0]
            u_sum[bi, bj] += ui
            v_sum[bi, bj] += vi
            counts[bi, bj] += 1
    with np.errstate(invalid="ignore", divide="ignore"):
        u_mean = np.where(counts > 0, u_sum / counts, np.nan)
        v_mean = np.where(counts > 0, v_sum / counts, np.nan)
    return xr.Dataset(
        {"water_u": (("lat", "lon"), u_mean), "water_v": (("lat", "lon"), v_mean)},
        coords={"lat": grid["lat"].values, "lon": grid["lon"].values},
    )


def aggregate_ndbc_sst_to_grid(ndbc: pd.DataFrame, grid: xr.Dataset) -> xr.Dataset:
    lat_col = "latitude" if "latitude" in ndbc.columns else "lat"
    lon_col = "longitude" if "longitude" in ndbc.columns else "lon"
    dlat = float(np.median(np.diff(grid["lat"].values))) if len(grid["lat"]) > 1 else 0.1
    dlon = float(np.median(np.diff(grid["lon"].values))) if len(grid["lon"]) > 1 else 0.1
    sums = np.zeros((len(grid["lat"]), len(grid["lon"])))
    counts = np.zeros_like(sums)
    for _, row in ndbc.iterrows():
        wtmp = row.get("WTMP")
        if wtmp is None or not np.isfinite(float(wtmp)):
            continue
        la, lo = float(row[lat_col]), float(row[lon_col])
        bi = int(np.argmin(np.abs(grid["lat"].values - la)))
        bj = int(np.argmin(np.abs(grid["lon"].values - lo)))
        if abs(grid["lat"].values[bi] - la) > dlat or abs(grid["lon"].values[bj] - lo) > dlon:
            continue
        sums[bi, bj] += float(wtmp)
        counts[bi, bj] += 1
    with np.errstate(invalid="ignore", divide="ignore"):
        sst = np.where(counts > 0, sums / counts, np.nan)
    return xr.Dataset({"sst_obs": (("lat", "lon"), sst)}, coords=grid.coords)


def _nearest_curvilinear(
    model_ds: xr.Dataset,
    lat_pts: np.ndarray,
    lon_pts: np.ndarray,
    var: str,
) -> np.ndarray:
    lat_g = model_ds["lat_rho"].values
    lon_g = model_ds["lon_rho"].values
    field = np.asarray(model_ds[var].values)
    out = np.full(lat_pts.shape, np.nan, dtype=float)
    if field.ndim == 0:
        return np.full(lat_pts.shape, float(field))
    while field.ndim > 2:
        field = field[0]
    for i, (la, lo) in enumerate(zip(lat_pts.ravel(), lon_pts.ravel(), strict=True)):
        dist = (lat_g - la) ** 2 + (lon_g - lo) ** 2
        ei, xi = np.unravel_index(np.nanargmin(dist), dist.shape)
        out.ravel()[i] = float(field[ei, xi])
    return out


def model_on_training_grid(model_ds: xr.Dataset, grid: xr.Dataset) -> xr.Dataset:
    lat_pts, lon_pts = np.meshgrid(grid["lat"].values, grid["lon"].values, indexing="ij")
    out: dict[str, tuple[tuple[str, str], np.ndarray]] = {}
    for var in ("sst", "u_east", "v_north"):
        if var not in model_ds:
            continue
        out[var] = (("lat", "lon"), _nearest_curvilinear(model_ds, lat_pts, lon_pts, var))
    return xr.Dataset(out, coords={"lat": grid["lat"], "lon": grid["lon"]})
