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
