"""WCOFS×GLORYS overlap pairing on synthetic grids (no network)."""

from __future__ import annotations

import datetime as dt

import numpy as np
import xarray as xr

from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    depth_grid_m,
    load_overlap_config,
    meteorological_season,
    overlap_dates,
    pair_overlap_from_synthetic,
    split_label,
)


def _synthetic_wcofs(n_eta: int = 4, n_xi: int = 4, n_s: int = 5) -> xr.Dataset:
    s_rho = (np.arange(1, n_s + 1) - n_s - 0.5) / n_s
    lat = np.linspace(33.0, 33.3, n_eta)
    lon = np.linspace(-120.5, -120.2, n_xi)
    lat2d = np.broadcast_to(lat[:, None], (n_eta, n_xi))
    lon2d = np.broadcast_to(lon[None, :], (n_eta, n_xi))
    temp = np.linspace(12, 18, n_s)[:, None, None] * np.ones((n_s, n_eta, n_xi))
    salt = np.full((n_s, n_eta, n_xi), 33.5)
    return xr.Dataset(
        {
            "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp[None, ...]),
            "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), salt[None, ...]),
            "zeta": (("eta_rho", "xi_rho"), np.zeros((n_eta, n_xi))),
            "h": (("eta_rho", "xi_rho"), np.full((n_eta, n_xi), 120.0)),
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


def test_overlap_config_day_count() -> None:
    cfg = load_overlap_config()
    days = overlap_dates(cfg)
    assert len(days) == int(cfg["overlap"]["expected_days"]) == 661


def test_split_and_season_labels() -> None:
    cfg = load_overlap_config()
    assert split_label(dt.date(2024, 9, 1), cfg) == "fit"
    assert split_label(dt.date(2025, 9, 1), cfg) == "test"
    assert meteorological_season(dt.date(2024, 12, 15)) == "winter"


def test_pair_overlap_synthetic_row_shape() -> None:
    cfg = load_overlap_config()
    lat_dst, lon_dst = glorys_target_grid(33.0, 33.4, -120.6, -120.1, resolution_deg=0.05)
    z_levels = np.array([0.0, 5.0, 10.0, 50.0])
    nj, ni = len(lat_dst), len(lon_dst)
    nz = z_levels.size
    thetao = 14.0 + 0.1 * z_levels[:, None, None] * np.ones((nz, nj, ni))
    so = 33.0 + 0.01 * z_levels[:, None, None] * np.ones((nz, nj, ni))
    day = dt.date(2024, 9, 2)
    df = pair_overlap_from_synthetic(
        day,
        _synthetic_wcofs(),
        thetao,
        so,
        z_levels,
        lat_dst,
        lon_dst,
        config=cfg,
    )
    assert len(df) == nj * ni
    assert "wcofs_T3m" in df.columns
    assert "glorys_T3m" in df.columns
    assert "wcofs_sst_grad" in df.columns
    assert "wcofs_front_distance_km" in df.columns
    assert "nearshore" in df.columns
    assert (df["split"] == "fit").all()
    grid = depth_grid_m(cfg)
    assert grid[0] == 0.0 and grid[-1] == 200.0 and grid[1] - grid[0] == 1.0
