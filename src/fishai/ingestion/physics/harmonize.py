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


def _glorys_cell_spacing(
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    *,
    resolution_deg: float | None = None,
) -> tuple[float, float]:
    fallback = resolution_deg if resolution_deg is not None else 1.0 / 12.0
    dlat = float(np.median(np.diff(lat_dst))) if lat_dst.size > 1 else fallback
    dlon = float(np.median(np.diff(lon_dst))) if lon_dst.size > 1 else fallback
    return dlat, dlon


def assign_glorys_cell_indices(
    lat_src: np.ndarray,
    lon_src: np.ndarray,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    *,
    resolution_deg: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Map each source point to a GLORYS cell index using half-open boxes.

    Lat in ``[lat_c - dlat/2, lat_c + dlat/2)``, lon in ``[lon_c - dlon/2, lon_c + dlon/2)``.
    """
    lat_src = np.asarray(lat_src, dtype=float)
    lon_src = np.asarray(lon_src, dtype=float)
    dlat, dlon = _glorys_cell_spacing(lat_dst, lon_dst, resolution_deg=resolution_deg)
    lat_lo = lat_dst - dlat / 2.0
    lon_lo = lon_dst - dlon / 2.0
    j_idx = np.full(lat_src.shape, -1, dtype=int)
    i_idx = np.full(lon_src.shape, -1, dtype=int)
    for j, la in enumerate(lat_dst):
        in_lat = (lat_src >= lat_lo[j]) & (lat_src < lat_lo[j] + dlat)
        if not np.any(in_lat):
            continue
        for i, lo in enumerate(lon_dst):
            in_box = in_lat & (lon_src >= lon_lo[i]) & (lon_src < lon_lo[i] + dlon)
            j_idx[in_box] = j
            i_idx[in_box] = i
    return j_idx, i_idx


def area_weighted_regrid(
    field: np.ndarray,
    lat_src: np.ndarray,
    lon_src: np.ndarray,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    *,
    wet_mask: np.ndarray | None = None,
    cell_area: np.ndarray | None = None,
    depth_reachable: np.ndarray | None = None,
    min_wet_fraction: float = 0.5,
    resolution_deg: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Area-weighted mean from curvilinear WCOFS rho cells onto a regular GLORYS grid.

    Each source cell is weighted by ``A = 1/(pm*pn)`` (or ``cell_area`` when supplied).
    Assignment uses half-open GLORYS boxes around cell centres.

    ``wet_fraction`` at each destination cell is
    ``sum(A | wet & depth_reachable) / sum(A | all cells in box, land included)``.
    The remapped field is NaN when ``wet_fraction < min_wet_fraction``; otherwise it is
    the area-weighted mean over wet, depth-reachable cells with finite ``field``.
    """
    field = np.asarray(field, dtype=float)
    lat_src = np.asarray(lat_src, dtype=float)
    lon_src = np.asarray(lon_src, dtype=float)
    if cell_area is None:
        area = np.ones_like(field, dtype=float)
    else:
        area = np.asarray(cell_area, dtype=float)
    wet = np.ones_like(field, dtype=bool) if wet_mask is None else np.asarray(wet_mask, dtype=bool)
    reachable = (
        np.ones_like(field, dtype=bool)
        if depth_reachable is None
        else np.asarray(depth_reachable, dtype=bool)
    )
    nj, ni = lat_dst.size, lon_dst.size
    out = np.full((nj, ni), np.nan, dtype=float)
    wet_frac = np.full((nj, ni), np.nan, dtype=float)
    j_idx, i_idx = assign_glorys_cell_indices(
        lat_src, lon_src, lat_dst, lon_dst, resolution_deg=resolution_deg
    )
    for j in range(nj):
        for i in range(ni):
            in_box = (j_idx == j) & (i_idx == i)
            if not np.any(in_box):
                continue
            a_box = area[in_box]
            denom = float(np.sum(a_box))
            if denom <= 0:
                continue
            contrib = in_box & wet & reachable
            wet_frac[j, i] = float(np.sum(area[contrib])) / denom
            if wet_frac[j, i] < min_wet_fraction:
                continue
            use = contrib & np.isfinite(field)
            if not np.any(use):
                continue
            w = area[use]
            out[j, i] = float(np.sum(w * field[use]) / np.sum(w))
    return out, wet_frac
