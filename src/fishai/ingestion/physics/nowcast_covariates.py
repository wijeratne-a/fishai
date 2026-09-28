"""Daily WCOFS nowcast covariates on the GLORYS grid for inference."""

from __future__ import annotations

from typing import Any

import xarray as xr

from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.wcofs_glorys_grid import (
    coarsen_wcofs_to_glorys,
    compute_wcofs_covariates_on_glorys_grid,
    covariates_to_xarray,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import depth_grid_m, load_overlap_config


def build_wcofs_nowcast_covariates_for_inference(
    ds_wcofs: xr.Dataset,
    *,
    config: dict[str, Any] | None = None,
    u10: xr.DataArray | None = None,
    v10: xr.DataArray | None = None,
) -> xr.Dataset:
    """
    Build gridded WCOFS physics covariates for operational nowcast / inference.

    Covariates are computed on the GLORYS ~1/12° grid after area-weighted coarsening.
    """
    cfg = config or load_overlap_config()
    bbox = cfg["pilot_bbox"]
    lat_dst, lon_dst = glorys_target_grid(
        float(bbox["lat_min"]),
        float(bbox["lat_max"]),
        float(bbox["lon_min"]),
        float(bbox["lon_max"]),
    )
    depth = depth_grid_m(cfg)
    gridded = coarsen_wcofs_to_glorys(ds_wcofs, lat_dst, lon_dst, depth)
    u_arr = v_arr = None
    if u10 is not None and v10 is not None:
        u_arr = u10.values
        v_arr = v10.values
    fields = compute_wcofs_covariates_on_glorys_grid(gridded, u10=u_arr, v10=v_arr)
    return covariates_to_xarray(gridded, fields)
