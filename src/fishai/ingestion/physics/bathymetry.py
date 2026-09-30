"""WCOFS ROMS bathymetry ``h`` on the GLORYS 1/12° pilot grid (training + inference parity)."""

from __future__ import annotations

import numpy as np

from fishai.ingestion.physics.covariates import (
    DROP_REASON_OUTSIDE_WCOFS_DOMAIN,
    DROP_REASON_WCOFS_LOW_WET_FRACTION,
)
from fishai.ingestion.physics.harmonize import glorys_target_grid

WCOFS_BOTTOM_DEPTH_VARIABLE = "h"
WCOFS_BOTTOM_DEPTH_SOURCE = "wcofs_roms"


def normalize_lon_for_axis(lon: float, lon_axis: np.ndarray) -> float:
    """Map sample longitude onto the grid axis convention (e.g. 0..360 vs -180..180)."""
    if lon_axis.size == 0:
        return lon
    lon_max = float(np.nanmax(lon_axis))
    if lon_max > 180.0 and lon < 0.0:
        return lon + 360.0
    if lon_max <= 180.0 and lon > 180.0:
        return lon - 360.0
    return lon


def nearest_glorys_cell_indices(
    lat: float,
    lon: float,
    lat_axis: np.ndarray,
    lon_axis: np.ndarray,
) -> tuple[int, int]:
    lon = normalize_lon_for_axis(lon, lon_axis)
    j = int(np.argmin(np.abs(lat_axis - lat)))
    i = int(np.argmin(np.abs(lon_axis - lon)))
    return j, i


def glorys_pilot_depth_grid(bbox: dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
    return glorys_target_grid(
        float(bbox["lat_min"]),
        float(bbox["lat_max"]),
        float(bbox["lon_min"]),
        float(bbox["lon_max"]),
    )


def sample_wcofs_h_bottom_depth_m(
    lat: float,
    lon: float,
    h_m: np.ndarray,
    lat_axis: np.ndarray,
    lon_axis: np.ndarray,
    *,
    has_source: np.ndarray,
    wet_fraction: np.ndarray,
    min_wet_fraction: float,
) -> tuple[float, str | None]:
    """
    Sample positive ROMS ``h`` (m) at ``lat``/``lon`` on the coarsened GLORYS grid.

    Returns ``(depth_m, drop_reason)``; depth is NaN when unavailable (never 0).
    """
    j, i = nearest_glorys_cell_indices(lat, lon, lat_axis, lon_axis)
    if not bool(has_source[j, i]):
        return float("nan"), DROP_REASON_OUTSIDE_WCOFS_DOMAIN
    wf = float(wet_fraction[j, i])
    if not np.isfinite(wf) or wf < float(min_wet_fraction):
        return float("nan"), DROP_REASON_WCOFS_LOW_WET_FRACTION
    val = float(h_m[j, i])
    if not np.isfinite(val) or val <= 0.0:
        return float("nan"), DROP_REASON_WCOFS_LOW_WET_FRACTION
    return val, None


def _coarse_glorys_cell_is_wet(
    j: int,
    i: int,
    h_m: np.ndarray,
    has_source: np.ndarray,
    wet_fraction: np.ndarray,
) -> bool:
    """True when the coarsened cell has any wet ROMS contribution and finite positive ``h``."""
    if not bool(has_source[j, i]):
        return False
    wf = float(wet_fraction[j, i])
    if not np.isfinite(wf) or wf <= 0.0:
        return False
    val = float(h_m[j, i])
    return np.isfinite(val) and val > 0.0


def sample_wcofs_h_audit_m(
    lat: float,
    lon: float,
    h_m: np.ndarray,
    lat_axis: np.ndarray,
    lon_axis: np.ndarray,
    *,
    has_source: np.ndarray,
    wet_fraction: np.ndarray,
) -> float:
    """
    Audit-only WCOFS ``h`` (m) at the nearest wet coarsened GLORYS cell.

    Ignores ``min_wet_fraction`` gating used for trainable ``bottom_depth_m``.
    Returns NaN when no wet cell exists within the WCOFS overlap grid.
    """
    j0, i0 = nearest_glorys_cell_indices(lat, lon, lat_axis, lon_axis)
    nj, ni = h_m.shape
    if _coarse_glorys_cell_is_wet(j0, i0, h_m, has_source, wet_fraction):
        return float(h_m[j0, i0])
    lon_norm = normalize_lon_for_axis(lon, lon_axis)
    best_dist2: float | None = None
    best_h = float("nan")
    max_r = max(nj, ni)
    for r in range(1, max_r + 1):
        found_at_r = False
        for dj in range(-r, r + 1):
            for di in range(-r, r + 1):
                if max(abs(dj), abs(di)) != r:
                    continue
                j, i = j0 + dj, i0 + di
                if j < 0 or j >= nj or i < 0 or i >= ni:
                    continue
                if not _coarse_glorys_cell_is_wet(j, i, h_m, has_source, wet_fraction):
                    continue
                cell_lat = float(lat_axis[j])
                cell_lon = float(lon_axis[i])
                dist2 = (cell_lat - lat) ** 2 + (cell_lon - lon_norm) ** 2
                if best_dist2 is None or dist2 < best_dist2:
                    best_dist2 = dist2
                    best_h = float(h_m[j, i])
                    found_at_r = True
        if found_at_r and best_dist2 is not None:
            return best_h
    return best_h
