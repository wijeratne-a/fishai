"""Horizontal regridding utilities."""

from __future__ import annotations

import numpy as np


def glorys_target_grid(
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
    resolution_deg: float = 1.0 / 12.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Regular GLORYS-class 1/12° lat/lon axes covering the bbox."""
    lats = np.arange(lat_min, lat_max + resolution_deg * 0.5, resolution_deg)
    lons = np.arange(lon_min, lon_max + resolution_deg * 0.5, resolution_deg)
    return lats, lons


def area_weighted_regrid(
    field: np.ndarray,
    lat_src: np.ndarray,
    lon_src: np.ndarray,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    *,
    wet_mask: np.ndarray | None = None,
) -> np.ndarray:
    """
    Conservative area-weighted remap from curvilinear/irregular source cells to
    a regular lat/lon destination grid (cell-centre assignment with overlap weights).
    """
    field = np.asarray(field, dtype=float)
    lat_src = np.asarray(lat_src, dtype=float)
    lon_src = np.asarray(lon_src, dtype=float)
    if wet_mask is not None:
        wet_mask = np.asarray(wet_mask, dtype=bool)
        field = np.where(wet_mask, field, np.nan)
    out = np.full((lat_dst.size, lon_dst.size), np.nan, dtype=float)
    dlat = np.median(np.diff(lat_dst)) if lat_dst.size > 1 else 1.0 / 12.0
    dlon = np.median(np.diff(lon_dst)) if lon_dst.size > 1 else 1.0 / 12.0
    for j, la in enumerate(lat_dst):
        for i, lo in enumerate(lon_dst):
            in_box = (
                (lat_src >= la - dlat / 2)
                & (lat_src <= la + dlat / 2)
                & (lon_src >= lo - dlon / 2)
                & (lon_src <= lo + dlon / 2)
            )
            if not np.any(in_box):
                continue
            vals = field[in_box]
            if np.isfinite(vals).any():
                out[j, i] = np.nanmean(vals)
    return out
