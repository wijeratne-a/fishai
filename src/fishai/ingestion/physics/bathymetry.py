"""GLORYS static bathymetry (deptho) on the 1/12° pilot grid."""

from __future__ import annotations

import numpy as np

from fishai.ingestion.physics.harmonize import glorys_target_grid


def nearest_glorys_cell_indices(
    lat: float,
    lon: float,
    lat_axis: np.ndarray,
    lon_axis: np.ndarray,
) -> tuple[int, int]:
    j = int(np.argmin(np.abs(lat_axis - lat)))
    i = int(np.argmin(np.abs(lon_axis - lon)))
    return j, i


def sample_deptho_nearest_cell(
    lat: float,
    lon: float,
    deptho: np.ndarray,
    lat_axis: np.ndarray,
    lon_axis: np.ndarray,
) -> float:
    """
    Sample positive seafloor depth (m) at ``lat``/``lon`` on the GLORYS grid.

    Uses nearest cell centre (same rule as WCOFS×GLORYS overlap bathymetry config).
    """
    j, i = nearest_glorys_cell_indices(lat, lon, lat_axis, lon_axis)
    val = float(deptho[j, i])
    if not np.isfinite(val) or val <= 0.0:
        return float("nan")
    return val


def glorys_pilot_depth_grid(bbox: dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
    return glorys_target_grid(
        float(bbox["lat_min"]),
        float(bbox["lat_max"]),
        float(bbox["lon_min"]),
        float(bbox["lon_max"]),
    )
