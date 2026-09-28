"""Nowcast evidence state when WCOFS wet_fraction is below threshold."""

from __future__ import annotations

import numpy as np
import xarray as xr

from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.nowcast_covariates import build_wcofs_nowcast_covariates_for_inference
from fishai.ingestion.physics.wcofs_glorys_grid import (
    EVIDENCE_STATE_UNKNOWN,
    UNKNOWN_REASON_INSUFFICIENT_MODEL_COVERAGE,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config


def _wcofs(n: int, wet_center: tuple[slice, slice] | None) -> xr.Dataset:
    s_rho = (np.arange(1, 5) - 5 - 0.5) / 5
    lat = np.linspace(33.05, 33.25, n)
    lon = np.linspace(-120.45, -120.25, n)
    lat2d = np.broadcast_to(lat[:, None], (n, n))
    lon2d = np.broadcast_to(lon[None, :], (n, n))
    temp = 15.0 + np.linspace(0, 2, 4)[:, None, None] * np.ones((4, n, n))
    mask = np.ones((n, n))
    if wet_center is not None:
        mask[:] = 0.0
        mask[wet_center] = 1.0
    return xr.Dataset(
        {
            "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp[None, ...]),
            "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), np.full((1, 4, n, n), 33.5)),
            "zeta": (("eta_rho", "xi_rho"), np.zeros((n, n))),
            "h": (("eta_rho", "xi_rho"), np.full((n, n), 100.0)),
            "mask_rho": (("eta_rho", "xi_rho"), mask),
            "lat_rho": (("eta_rho", "xi_rho"), lat2d),
            "lon_rho": (("eta_rho", "xi_rho"), lon2d),
            "pm": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
            "pn": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
            "hc": 50.0,
            "s_rho": ("s_rho", s_rho),
            "Cs_r": ("s_rho", np.linspace(-1, 0, 4)),
        }
    )


def test_mostly_land_box_marks_unknown_insufficient_coverage() -> None:
    cfg = load_overlap_config()
    lat_dst, lon_dst = glorys_target_grid(33.0, 33.3, -120.5, -120.2, resolution_deg=0.05)
    ds = _wcofs(8, wet_center=(slice(3, 5), slice(3, 5)))
    out = build_wcofs_nowcast_covariates_for_inference(
        ds, config=cfg, lat_dst=lat_dst, lon_dst=lon_dst
    )
    unknown = out["evidence_state"].values == EVIDENCE_STATE_UNKNOWN
    assert unknown.any()
    assert (
        out["unknown_reason"].values[unknown] == UNKNOWN_REASON_INSUFFICIENT_MODEL_COVERAGE
    ).all()


def test_fully_wet_box_does_not_mark_unknown() -> None:
    cfg = load_overlap_config()
    lat_dst, lon_dst = glorys_target_grid(33.0, 33.3, -120.5, -120.2, resolution_deg=0.05)
    ds = _wcofs(10, wet_center=None)
    out = build_wcofs_nowcast_covariates_for_inference(
        ds, config=cfg, lat_dst=lat_dst, lon_dst=lon_dst
    )
    interior = out["evidence_state"].values[1:-1, 1:-1]
    assert (interior != EVIDENCE_STATE_UNKNOWN).any()
