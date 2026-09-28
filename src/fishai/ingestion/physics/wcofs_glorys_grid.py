"""
Coarsen WCOFS onto the GLORYS ~1/12° grid and compute shared physics covariates.

Used by the WCOFS×GLORYS overlap pairing path and the daily WCOFS nowcast inference path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import xarray as xr

from fishai.ingestion.physics.features import ekman_upwelling, front_distance_km, sst_gradient
from fishai.ingestion.physics.harmonize import area_weighted_regrid
from fishai.ingestion.physics.vertical import interp_at_depth_from_z_levels, mld, s_to_z

COVARIATE_FIELDS = ("T3m", "S3m", "MLD_m", "sst_grad", "front_distance_km", "upwelling")

# Harmonization buoy SST matching depth (below moving sea surface); see prereg surface_definition.
HARMONIZATION_BUOY_MATCH_DEPTH_M = 0.494


def harmonization_temperature_at_buoy_depth(
    depth_levels_m: np.ndarray,
    temperature: np.ndarray,
    *,
    depth_m: float = HARMONIZATION_BUOY_MATCH_DEPTH_M,
) -> float:
    """
    Shared depth function for all four harmonization model rows at NDBC buoys.

    Linear interpolation in depth below the moving surface (positive metres down).
    """
    return interp_at_depth_from_z_levels(depth_levels_m, temperature, depth_m)


@dataclass(frozen=True)
class WcofsGlorysGrid:
    """WCOFS tracers area-averaged onto a regular lat/lon GLORYS-class grid."""

    lat: np.ndarray
    lon: np.ndarray
    depth_m: np.ndarray
    temp: np.ndarray
    salt: np.ndarray


def _surface_slab(ds: xr.Dataset) -> xr.Dataset:
    if "lead_hours" in ds.dims:
        ds = ds.isel(lead_hours=0)
    return ds.isel(ocean_time=0) if "ocean_time" in ds.dims else ds


def _native_profiles_on_depth_grid(
    slab: xr.Dataset,
    depth_grid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    ref = _surface_slab(slab)
    h = ref.h.values
    zeta = ref.zeta.values
    temp = ref.temp.values
    salt = ref.salt.values
    if temp.ndim == 4:
        temp = temp[0]
        salt = salt[0]
    s_rho = ref.s_rho.values
    hc = float(ref.hc.values)
    cs_r = ref.Cs_r.values if "Cs_r" in ref else None
    z_roms = s_to_z(h, zeta, s_rho, hc, cs_r=cs_r)
    depth = -z_roms
    ny, nx, nz = depth.shape[1], depth.shape[2], depth.shape[0]
    temp_out = np.full((ny, nx, depth_grid.size), np.nan)
    salt_out = np.full((ny, nx, depth_grid.size), np.nan)
    for j in range(ny):
        for i in range(nx):
            dcol = depth[:, j, i]
            tcol = temp[:, j, i]
            scol = salt[:, j, i]
            order = np.argsort(dcol)
            d_sorted = dcol[order]
            temp_out[j, i, :] = np.interp(
                depth_grid, d_sorted, tcol[order], left=np.nan, right=np.nan
            )
            salt_out[j, i, :] = np.interp(
                depth_grid, d_sorted, scol[order], left=np.nan, right=np.nan
            )
    return temp_out, salt_out


def coarsen_wcofs_to_glorys(
    ds_wcofs: xr.Dataset,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    depth_grid_m: np.ndarray,
) -> WcofsGlorysGrid:
    """
    Area-weighted average of ocean-only (wet) WCOFS cells onto ``lat_dst`` × ``lon_dst``.

    Tracers are linearly interpolated to ``depth_grid_m`` on the native grid first, then
    each depth level is coarsened independently with the ROMS wet mask.
    """
    slab = _surface_slab(ds_wcofs)
    lat = np.asarray(slab.lat_rho.values, dtype=float)
    lon = np.asarray(slab.lon_rho.values, dtype=float)
    lon = np.where(lon > 180, lon - 360, lon)
    wet = np.asarray(slab.mask_rho.values == 1, dtype=bool)
    temp_native, salt_native = _native_profiles_on_depth_grid(slab, depth_grid_m)
    nj, ni = lat_dst.size, lon_dst.size
    nz = depth_grid_m.size
    temp_coarse = np.full((nj, ni, nz), np.nan, dtype=float)
    salt_coarse = np.full((nj, ni, nz), np.nan, dtype=float)
    for k in range(nz):
        temp_coarse[:, :, k] = area_weighted_regrid(
            temp_native[:, :, k], lat, lon, lat_dst, lon_dst, wet_mask=wet
        )
        salt_coarse[:, :, k] = area_weighted_regrid(
            salt_native[:, :, k], lat, lon, lat_dst, lon_dst, wet_mask=wet
        )
    return WcofsGlorysGrid(
        lat=np.asarray(lat_dst, dtype=float),
        lon=np.asarray(lon_dst, dtype=float),
        depth_m=np.asarray(depth_grid_m, dtype=float),
        temp=temp_coarse,
        salt=salt_coarse,
    )


def compute_wcofs_covariates_on_glorys_grid(
    gridded: WcofsGlorysGrid,
    *,
    u10: np.ndarray | None = None,
    v10: np.ndarray | None = None,
) -> dict[str, np.ndarray]:
    """
    Compute model covariates on the GLORYS grid from coarsened WCOFS tracers.

    Features are computed only after coarsening (never on the native ~4 km grid).
    """
    nj, ni, nz = gridded.temp.shape
    depth = gridded.depth_m
    t3m = np.full((nj, ni), np.nan, dtype=float)
    s3m = np.full((nj, ni), np.nan, dtype=float)
    mld_m = np.full((nj, ni), np.nan, dtype=float)
    for j in range(nj):
        for i in range(ni):
            tp = gridded.temp[j, i, :]
            sp = gridded.salt[j, i, :]
            if not np.isfinite(tp).any():
                continue
            t3m[j, i] = interp_at_depth_from_z_levels(depth, tp, 3.0)
            s3m[j, i] = interp_at_depth_from_z_levels(depth, sp, 3.0)
            z3d = (-depth)[:, None, None]
            mld_m[j, i] = float(mld(z3d, tp[:, None, None])[0, 0])
    sst = gridded.temp[:, :, 0]
    grad = sst_gradient(sst, gridded.lat, gridded.lon)
    lat2d, lon2d = np.meshgrid(gridded.lat, gridded.lon, indexing="ij")
    front_km = front_distance_km(grad, lat2d, lon2d)
    if u10 is not None and v10 is not None:
        ek = ekman_upwelling(u10, v10, lat2d)
        upwelling = ek.get("coastal_upwelling_index", ek["ekman_pumping"])
    else:
        upwelling = np.full((nj, ni), np.nan, dtype=float)
    return {
        "T3m": t3m,
        "S3m": s3m,
        "MLD_m": mld_m,
        "sst_grad": grad,
        "front_distance_km": front_km,
        "upwelling": upwelling,
    }


def wcofs_native_4km_covariates_diagnostic(
    ds_wcofs: xr.Dataset,
    depth_grid_m: np.ndarray,
) -> dict[str, np.ndarray]:
    """
    Native WCOFS rho-grid covariates (diagnostic only; not used for nowcast inference).
    """
    slab = _surface_slab(ds_wcofs)
    temp_native, salt_native = _native_profiles_on_depth_grid(slab, depth_grid_m)
    ny, nx, _ = temp_native.shape
    depth = depth_grid_m
    out: dict[str, np.ndarray] = {k: np.full((ny, nx), np.nan) for k in COVARIATE_FIELDS}
    lat = slab.lat_rho.values
    lon = slab.lon_rho.values
    sst = np.full((ny, nx), np.nan)
    for j in range(ny):
        for i in range(nx):
            tp = temp_native[j, i, :]
            sp = salt_native[j, i, :]
            if not np.isfinite(tp).any():
                continue
            out["T3m"][j, i] = interp_at_depth_from_z_levels(depth, tp, 3.0)
            out["S3m"][j, i] = interp_at_depth_from_z_levels(depth, sp, 3.0)
            z3d = (-depth)[:, None, None]
            out["MLD_m"][j, i] = float(mld(z3d, tp[:, None, None])[0, 0])
            sst[j, i] = tp[0]
    out["sst_grad"] = sst_gradient(sst, lat, lon)
    out["front_distance_km"] = front_distance_km(out["sst_grad"], lat, lon)
    out["upwelling"] = np.full((ny, nx), np.nan)
    return out


def covariates_to_xarray(
    gridded: WcofsGlorysGrid,
    fields: dict[str, np.ndarray],
) -> xr.Dataset:
    return xr.Dataset(
        {name: (("lat", "lon"), arr) for name, arr in fields.items()},
        coords={"lat": gridded.lat, "lon": gridded.lon},
        attrs={"grid": "glorys_1_12deg", "depth_grid_m": gridded.depth_m.tolist()},
    )
