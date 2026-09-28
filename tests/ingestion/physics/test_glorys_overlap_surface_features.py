"""GLORYS overlap rows must compute sst_grad and front_distance_km (not hard-coded NaN)."""

from __future__ import annotations

import datetime as dt

import numpy as np

from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.wcofs_glorys_grid import compute_glorys_covariates_on_glorys_grid
from fishai.ingestion.physics.wcofs_glorys_overlap import pair_overlap_from_synthetic
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
from tests.ingestion.physics.test_wcofs_glorys_overlap import _synthetic_wcofs


def test_glorys_sst_grad_and_front_distance_computed_on_grid() -> None:
    cfg = load_overlap_config()
    lat_dst, lon_dst = glorys_target_grid(33.0, 33.4, -120.6, -120.1, resolution_deg=0.05)
    z_levels = np.array([0.0, 0.49, 3.0, 10.0, 50.0])
    nj, ni = len(lat_dst), len(lon_dst)
    nz = z_levels.size
    thetao = 14.0 + 0.2 * z_levels[:, None, None] * np.ones((nz, nj, ni))
    so = 33.0 + 0.01 * z_levels[:, None, None] * np.ones((nz, nj, ni))
    gridded = compute_glorys_covariates_on_glorys_grid(z_levels, thetao, so, lat_dst, lon_dst)
    assert np.isfinite(gridded["sst_grad"]).any()
    assert np.isfinite(gridded["front_distance_km"]).any()


def test_overlap_dataframe_includes_finite_glorys_surface_metrics() -> None:
    cfg = load_overlap_config()
    lat_dst, lon_dst = glorys_target_grid(33.0, 33.35, -120.55, -120.15, resolution_deg=0.05)
    z_levels = np.array([0.0, 0.49, 3.0, 10.0, 50.0])
    nj, ni = len(lat_dst), len(lon_dst)
    nz = z_levels.size
    thetao = 14.0 + 0.15 * z_levels[:, None, None] * np.ones((nz, nj, ni))
    so = np.full((nz, nj, ni), 33.2)
    df = pair_overlap_from_synthetic(
        dt.date(2024, 9, 2),
        _synthetic_wcofs(),
        thetao,
        so,
        z_levels,
        lat_dst,
        lon_dst,
        config=cfg,
    )
    assert "glorys_sst_grad" in df.columns
    assert np.isfinite(df["glorys_sst_grad"]).any()
    assert np.isfinite(df["glorys_front_distance_km"]).any()
