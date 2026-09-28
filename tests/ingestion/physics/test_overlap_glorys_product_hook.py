"""Overlap pairing must use ``glorys_dataset_id_for_date`` (PR #7), not duplicated logic."""

from __future__ import annotations

import datetime as dt
from unittest.mock import patch

import numpy as np
import xarray as xr

from fishai.ingestion.physics.sources.glorys import (
    PRODUCT_ID_MYINT,
    glorys_dataset_id_for_date,
    glorys_product_for_date,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    glorys_grid_from_config,
    load_overlap_config,
    run_overlap_pairing,
)


def _tiny_wcofs() -> xr.Dataset:
    n = 4
    s_rho = (np.arange(1, 4) - 4 - 0.5) / 4
    lat = np.linspace(33.05, 33.2, n)
    lon = np.linspace(-120.4, -120.25, n)
    lat2d = np.broadcast_to(lat[:, None], (n, n))
    lon2d = np.broadcast_to(lon[None, :], (n, n))
    temp = 15.0 + np.linspace(0, 1, 3)[:, None, None] * np.ones((3, n, n))
    return xr.Dataset(
        {
            "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp[None, ...]),
            "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), np.full((1, 3, n, n), 33.5)),
            "zeta": (("eta_rho", "xi_rho"), np.zeros((n, n))),
            "h": (("eta_rho", "xi_rho"), np.full((n, n), 100.0)),
            "mask_rho": (("eta_rho", "xi_rho"), np.ones((n, n))),
            "lat_rho": (("eta_rho", "xi_rho"), lat2d),
            "lon_rho": (("eta_rho", "xi_rho"), lon2d),
            "pm": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
            "pn": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
            "hc": 50.0,
            "s_rho": ("s_rho", s_rho),
            "Cs_r": ("s_rho", np.linspace(-1, 0, 3)),
        }
    )


def test_run_overlap_pairing_calls_glorys_dataset_id_for_date(tmp_path) -> None:
    cfg = load_overlap_config()
    cfg = dict(cfg)
    cfg["pilot_bbox"] = {
        "lat_min": 33.0,
        "lat_max": 33.3,
        "lon_min": -120.5,
        "lon_max": -120.2,
    }
    cfg["coverage_report"] = {
        **cfg.get("coverage_report", {}),
        "json_path": str(tmp_path / "coverage_report.json"),
        "csv_path": str(tmp_path / "coverage_cells.csv"),
    }
    z_levels = np.array([0.0, 3.0, 10.0])

    def glorys_fetch(_day: dt.date) -> dict:
        la, lo = glorys_grid_from_config(cfg)
        nj, ni = la.size, lo.size
        nz = z_levels.size
        return {
            "thetao": 14.0 + 0.1 * z_levels[:, None, None] * np.ones((nz, nj, ni)),
            "so": np.full((nz, nj, ni), 33.5),
            "depth": z_levels,
        }

    with patch(
        "fishai.ingestion.physics.wcofs_glorys_overlap.glorys_dataset_id_for_date",
        wraps=glorys_dataset_id_for_date,
    ) as mocked:
        run_overlap_pairing(
            config=cfg,
            days=[dt.date(2024, 9, 1)],
            wcofs_open=lambda _d: _tiny_wcofs(),
            glorys_fetch=glorys_fetch,
            wcofs_log=tmp_path / "wcofs_pull_log.jsonl",
            glorys_log=tmp_path / "copernicus_pull_log.jsonl",
        )
        mocked.assert_called_with(dt.date(2024, 9, 1), config=cfg)
        assert glorys_product_for_date(dt.date(2024, 9, 1), config=cfg) == PRODUCT_ID_MYINT
