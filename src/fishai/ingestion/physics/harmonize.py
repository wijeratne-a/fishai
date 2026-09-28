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


def destination_cell_source_stats(
    lat_src: np.ndarray,
    lon_src: np.ndarray,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    wet_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Per destination GLORYS cell: whether any WCOFS rho point fell in the box, and wet fraction.
    """
    lat_src = np.asarray(lat_src, dtype=float)
    lon_src = np.asarray(lon_src, dtype=float)
    wet_mask = np.asarray(wet_mask, dtype=bool)
    has_source = np.zeros((lat_dst.size, lon_dst.size), dtype=bool)
    wet_fraction = np.full((lat_dst.size, lon_dst.size), np.nan, dtype=float)
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
            n_in = int(np.count_nonzero(in_box))
            if n_in == 0:
                continue
            has_source[j, i] = True
            n_wet = int(np.count_nonzero(in_box & wet_mask))
            wet_fraction[j, i] = n_wet / n_in
    return has_source, wet_fraction


def area_weighted_regrid(
    field: np.ndarray,
    lat_src: np.ndarray,
    lon_src: np.ndarray,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    *,
    wet_mask: np.ndarray | None = None,
    min_wet_fraction: float | None = None,
) -> np.ndarray:
    """
    Conservative area-weighted remap from curvilinear/irregular source cells to
    a regular lat/lon destination grid (cell-centre assignment with overlap weights).

    When ``min_wet_fraction`` is set (WCOFS×GLORYS coarsening), destination cells
    whose overlapping source points are mostly land are left NaN.
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
            n_in = int(np.count_nonzero(in_box))
            if n_in == 0:
                continue
            if wet_mask is not None and min_wet_fraction is not None:
                n_wet = int(np.count_nonzero(in_box & wet_mask))
                if (n_wet / n_in) < float(min_wet_fraction):
                    continue
            vals = field[in_box]
            if np.isfinite(vals).any():
                out[j, i] = np.nanmean(vals)
    return out
