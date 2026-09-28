"""Overlap and nowcast paths must share identical GLORYS-grid WCOFS covariates."""

from __future__ import annotations

import datetime as dt

import numpy as np
import xarray as xr

from fishai.ingestion.physics.nowcast_covariates import build_wcofs_nowcast_covariates_for_inference
from fishai.ingestion.physics.wcofs_glorys_grid import COVARIATE_FIELDS
from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    load_overlap_config,
    wcofs_covariate_arrays_on_glorys_grid,
)


def _synthetic_wcofs(n_eta: int = 12, n_xi: int = 12, n_s: int = 6) -> xr.Dataset:
    s_rho = (np.arange(1, n_s + 1) - n_s - 0.5) / n_s
    lat = np.linspace(33.0, 33.35, n_eta)
    lon = np.linspace(-120.55, -120.15, n_xi)
    lat2d = np.broadcast_to(lat[:, None], (n_eta, n_xi))
    lon2d = np.broadcast_to(lon[None, :], (n_eta, n_xi))
    temp = np.linspace(12, 19, n_s)[:, None, None] * np.ones((n_s, n_eta, n_xi))
    salt = 33.0 + 0.02 * np.linspace(0, 1, n_s)[:, None, None] * np.ones((n_s, n_eta, n_xi))
    return xr.Dataset(
        {
            "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp[None, ...]),
            "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), salt[None, ...]),
            "zeta": (("eta_rho", "xi_rho"), np.zeros((n_eta, n_xi))),
            "h": (("eta_rho", "xi_rho"), np.full((n_eta, n_xi), 150.0)),
            "mask_rho": (("eta_rho", "xi_rho"), np.ones((n_eta, n_xi))),
            "lat_rho": (("eta_rho", "xi_rho"), lat2d),
            "lon_rho": (("eta_rho", "xi_rho"), lon2d),
            "pm": (("eta_rho", "xi_rho"), np.full((n_eta, n_xi), 1.0 / 3500.0)),
            "pn": (("eta_rho", "xi_rho"), np.full((n_eta, n_xi), 1.0 / 3500.0)),
            "hc": 50.0,
            "s_rho": ("s_rho", s_rho),
            "Cs_r": ("s_rho", np.linspace(-1, 0, n_s)),
        }
    )


def test_overlap_and_nowcast_paths_match_on_synthetic_cycle() -> None:
    cfg = load_overlap_config()
    lat_dst, lon_dst = glorys_target_grid(33.0, 33.4, -120.6, -120.1, resolution_deg=0.05)
    ds = _synthetic_wcofs()
    overlap = wcofs_covariate_arrays_on_glorys_grid(ds, lat_dst, lon_dst, cfg)
    nowcast = build_wcofs_nowcast_covariates_for_inference(
        ds, config=cfg, lat_dst=lat_dst, lon_dst=lon_dst
    )
    for field in COVARIATE_FIELDS:
        o = overlap[field]
        n = nowcast[field].values
        np.testing.assert_array_equal(o, n)
        if field in ("sst_grad", "front_distance_km"):
            finite_o = np.isfinite(o)
            finite_n = np.isfinite(n)
            assert finite_o.sum() > 0
            assert finite_n.sum() > 0
            assert finite_o.mean() > 0.25
            assert finite_n.mean() > 0.25
