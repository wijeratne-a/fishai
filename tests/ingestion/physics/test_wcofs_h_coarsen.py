"""WCOFS ROMS ``h`` coarsening onto the GLORYS grid."""

from __future__ import annotations

import numpy as np
import xarray as xr

from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.wcofs_glorys_grid import coarsen_wcofs_h_to_glorys


def _synthetic_wcofs(n_eta: int = 6, n_xi: int = 6) -> xr.Dataset:
    lat = np.linspace(33.0, 33.5, n_eta)
    lon = np.linspace(-120.5, -120.0, n_xi)
    lat2d = np.broadcast_to(lat[:, None], (n_eta, n_xi))
    lon2d = np.broadcast_to(lon[None, :], (n_eta, n_xi))
    h = np.full((n_eta, n_xi), 120.0)
    h[0, 0] = np.nan
    mask = np.ones((n_eta, n_xi))
    mask[0, 0] = 0
    return xr.Dataset(
        {
            "h": (("eta_rho", "xi_rho"), h),
            "mask_rho": (("eta_rho", "xi_rho"), mask),
            "lat_rho": (("eta_rho", "xi_rho"), lat2d),
            "lon_rho": (("eta_rho", "xi_rho"), lon2d),
            "zeta": (("eta_rho", "xi_rho"), np.zeros((n_eta, n_xi))),
        }
    )


def test_coarsen_h_respects_min_wet_fraction() -> None:
    lat_dst, lon_dst = glorys_target_grid(33.0, 33.5, -120.6, -119.9, resolution_deg=0.1)
    h_m, has_source, wet_fraction = coarsen_wcofs_h_to_glorys(
        _synthetic_wcofs(),
        lat_dst,
        lon_dst,
        min_wet_fraction=0.5,
    )
    assert has_source.any()
    assert np.isfinite(h_m[has_source]).any()
    assert (h_m[~has_source] != 0).all() or np.isnan(h_m[~has_source]).all()
    assert np.nanmax(wet_fraction[has_source]) <= 1.0
