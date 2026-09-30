"""Daily WCOFS nowcast covariates on the GLORYS grid for inference."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import xarray as xr

from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.wcofs_glorys_grid import (
    coarsen_wcofs_to_glorys,
    compute_wcofs_covariates_on_glorys_grid,
    covariates_to_xarray,
    inference_evidence_masks,
    min_wet_fraction_from_config,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import depth_grid_m, load_overlap_config
from fishai.physics.store import open_wcofs_cycle_for_operational_day


def load_wcofs_dataset_for_operational_nowcast(
    cycle_date: dt.date | None = None,
    *,
    store_root: Path | None = None,
) -> xr.Dataset:
    """Load processed WCOFS for ``cycle_date`` (default UTC today); never an older cycle."""
    return open_wcofs_cycle_for_operational_day(cycle_date, store_root=store_root)


def build_wcofs_nowcast_covariates_for_inference(
    ds_wcofs: xr.Dataset,
    *,
    config: dict[str, Any] | None = None,
    lat_dst: Any | None = None,
    lon_dst: Any | None = None,
    u10: xr.DataArray | None = None,
    v10: xr.DataArray | None = None,
) -> xr.Dataset:
    """
    Build gridded WCOFS physics covariates for operational nowcast / inference.

    Covariates are computed on the GLORYS ~1/12° grid after area-weighted coarsening.
    """
    cfg = config or load_overlap_config()
    if lat_dst is None or lon_dst is None:
        bbox = cfg["pilot_bbox"]
        lat_dst, lon_dst = glorys_target_grid(
            float(bbox["lat_min"]),
            float(bbox["lat_max"]),
            float(bbox["lon_min"]),
            float(bbox["lon_max"]),
        )
    depth = depth_grid_m(cfg)
    gridded = coarsen_wcofs_to_glorys(
        ds_wcofs,
        lat_dst,
        lon_dst,
        depth,
        min_wet_fraction=min_wet_fraction_from_config(cfg),
    )
    u_arr = v_arr = None
    if u10 is not None and v10 is not None:
        u_arr = u10.values
        v_arr = v10.values
    min_wf = min_wet_fraction_from_config(cfg)
    fields = compute_wcofs_covariates_on_glorys_grid(gridded, u10=u_arr, v10=v_arr)
    evidence_state, unknown_reason = inference_evidence_masks(gridded, min_wet_fraction=min_wf)
    fields["evidence_state"] = evidence_state
    fields["unknown_reason"] = unknown_reason
    return covariates_to_xarray(gridded, fields)
