"""Synthetic GLORYS grids for unit tests only (never Copernicus-attributed)."""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterable
from typing import Any

import numpy as np

from fishai.ingestion.physics.cufes_training_covariates import (
    GlorysDayFields,
    GlorysFieldStore,
    _compute_day_surface_fields,
)
from fishai.ingestion.physics.glorys_training_build import SYNTHETIC_TEST_FIXTURE_SOURCE
from fishai.ingestion.physics.bathymetry import glorys_pilot_depth_grid
from fishai.ingestion.physics.sources.glorys import glorys_product_for_date
from fishai.ingestion.physics.wcofs_glorys_overlap import coarsen_min_wet_fraction, load_overlap_config


def build_synthetic_day_fields(
    day: dt.date,
    lat: np.ndarray,
    lon: np.ndarray,
    *,
    nz: int = 5,
) -> GlorysDayFields:
    if nz == 5:
        depth_levels = np.array([50.0, 20.0, 10.0, 5.0, 0.0])
        base_temp = np.array([10.0, 15.0, 17.8, 17.9, 18.0])
    else:
        depth_levels = np.linspace(0.0, 50.0, nz)
        base_temp = 18.5 - 0.12 * depth_levels
    nj, ni = lat.size, lon.size
    lat2d = lat[:, None] + np.zeros((nj, ni))
    lon2d = lon[None, :] + np.zeros((nj, ni))
    thetao = np.stack(
        [base_temp[k] + 0.03 * lat2d + 0.01 * lon2d for k in range(depth_levels.size)],
        axis=0,
    )
    so = np.stack(
        [33.5 + 0.0005 * lat2d for _ in range(depth_levels.size)],
        axis=0,
    )
    mlotst = np.full((nj, ni), 20.0)
    product_id = glorys_product_for_date(day)
    return _compute_day_surface_fields(
        day,
        product_id,
        lat,
        lon,
        depth_levels,
        thetao,
        so,
        mlotst,
    )


def glorys_store_from_synthetic_days(
    days: Iterable[dt.date],
    *,
    config: dict[str, Any] | None = None,
    wcofs_h_m: np.ndarray | None = None,
    has_source: np.ndarray | None = None,
    wet_fraction: np.ndarray | None = None,
    lat: np.ndarray | None = None,
    lon: np.ndarray | None = None,
    roms_hmin_m: float | None = None,
    hmin_source: str = "wet_cell_minimum_h",
    wind_source_id: str = "ccmp_winds",
) -> GlorysFieldStore:
    cfg = config or load_overlap_config()
    min_wet = coarsen_min_wet_fraction(cfg)
    if lat is None or lon is None:
        bbox = cfg["pilot_bbox"]
        lat, lon = glorys_pilot_depth_grid(bbox)
    nj, ni = lat.size, lon.size
    if wcofs_h_m is None:
        wcofs_h_m = np.full((nj, ni), 500.0)
    if has_source is None:
        has_source = np.ones((nj, ni), dtype=bool)
    if roms_hmin_m is None:
        wet_vals = wcofs_h_m[has_source]
        finite = wet_vals[np.isfinite(wet_vals) & (wet_vals > 0)]
        roms_hmin_m = float(np.min(finite)) if finite.size else float("nan")
    if wet_fraction is None:
        wet_fraction = np.ones((nj, ni), dtype=float)
    store = GlorysFieldStore(
        wcofs_h_m=wcofs_h_m,
        has_source=has_source,
        wet_fraction=wet_fraction,
        min_wet_fraction=min_wet,
        roms_hmin_m=float(roms_hmin_m),
        hmin_source=hmin_source,
        lat=lat,
        lon=lon,
        wind_source_id=wind_source_id,
        covariate_data_source=SYNTHETIC_TEST_FIXTURE_SOURCE,
        days={},
    )
    for day in days:
        store.days[day] = build_synthetic_day_fields(day, lat, lon)
    return store
