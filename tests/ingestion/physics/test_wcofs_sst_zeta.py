"""SST and fronts stay finite when zeta shifts the free surface."""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    depth_grid_m,
    load_overlap_config,
    wcofs_covariate_arrays_on_glorys_grid,
)


def _synthetic_wcofs(zeta_value: float) -> xr.Dataset:
    n_eta, n_xi, n_s = 12, 12, 8
    s_rho = (np.arange(1, n_s + 1) - n_s - 0.5) / n_s
    lat = np.linspace(33.0, 33.35, n_eta)
    lon = np.linspace(-120.55, -120.15, n_xi)
    lat2d = np.broadcast_to(lat[:, None], (n_eta, n_xi))
    lon2d = np.broadcast_to(lon[None, :], (n_eta, n_xi))
    temp = np.linspace(12, 19, n_s)[:, None, None] * np.ones((n_s, n_eta, n_xi))
    salt = np.full((n_s, n_eta, n_xi), 33.5)
    pm = np.full((n_eta, n_xi), 1.0 / 3000.0)
    pn = np.full((n_eta, n_xi), 1.0 / 3000.0)
    return xr.Dataset(
        {
            "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp[None, ...]),
            "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), salt[None, ...]),
            "zeta": (("eta_rho", "xi_rho"), np.full((n_eta, n_xi), zeta_value)),
            "h": (("eta_rho", "xi_rho"), np.full((n_eta, n_xi), 80.0)),
            "mask_rho": (("eta_rho", "xi_rho"), np.ones((n_eta, n_xi))),
            "lat_rho": (("eta_rho", "xi_rho"), lat2d),
            "lon_rho": (("eta_rho", "xi_rho"), lon2d),
            "pm": (("eta_rho", "xi_rho"), pm),
            "pn": (("eta_rho", "xi_rho"), pn),
            "hc": 50.0,
            "s_rho": ("s_rho", s_rho),
            "Cs_r": ("s_rho", np.linspace(-1, 0, n_s)),
        }
    )


@pytest.mark.parametrize("zeta", [-0.4, 0.0, 0.4])
def test_sst_grad_and_front_finite_on_wet_interior(zeta: float) -> None:
    cfg = load_overlap_config()
    lat_dst, lon_dst = glorys_target_grid(33.0, 33.4, -120.6, -120.1, resolution_deg=0.05)
    fields = wcofs_covariate_arrays_on_glorys_grid(
        _synthetic_wcofs(zeta), lat_dst, lon_dst, cfg
    )
    grad = fields["sst_grad"]
    front = fields["front_distance_km"]
    wet = np.isfinite(fields["T3m"][2:-2, 2:-2])
    assert wet.any()
    assert np.isfinite(grad[2:-2, 2:-2][wet]).all()
    assert np.isfinite(front[2:-2, 2:-2][wet]).all()
