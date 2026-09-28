"""Coastal upwelling from shared 10 m wind product (GLORYS vs WCOFS paths)."""

from __future__ import annotations

import datetime as dt
import json
import math
from unittest.mock import patch

import numpy as np
import pyarrow.parquet as pq
import xarray as xr

from fishai.ingestion.physics.cufes_training_covariates import (
    _compute_day_surface_fields,
    glorys_store_from_synthetic_days,
    write_training_covariates_parquet,
)
from fishai.ingestion.physics.features import (
    PILOT_COAST_ANGLE_DEG,
    PILOT_COAST_ANGLE_RAD,
    UPWELLING_FORMULA_ID,
    compute_upwelling,
)
from fishai.ingestion.physics.sources.glorys import glorys_product_for_date
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    glorys_grid_from_config,
    load_overlap_config,
    wcofs_covariate_arrays_on_glorys_grid,
)
from fishai.ingestion.sources import require_approved


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


def _equatorward_alongshore_wind(speed_m_s: float, shape: tuple[int, ...]) -> tuple[np.ndarray, np.ndarray]:
    """Wind blowing equatorward along the pilot mainland coast tangent."""
    sc = math.cos(PILOT_COAST_ANGLE_RAD)
    sn = math.sin(PILOT_COAST_ANGLE_RAD)
    u10 = np.full(shape, -speed_m_s * sc, dtype=float)
    v10 = np.full(shape, -speed_m_s * sn, dtype=float)
    return u10, v10


def test_compute_upwelling_equatorward_alongshore_is_positive() -> None:
    u10, v10 = _equatorward_alongshore_wind(12.0, (3, 4))
    lat = np.linspace(33.0, 33.5, 3)
    ui = compute_upwelling(u10, v10, lat)
    assert np.nanmin(ui) > 0.0


def test_glorys_and_wcofs_paths_use_same_compute_upwelling_and_wind() -> None:
    cfg = load_overlap_config()
    lat, lon = glorys_grid_from_config(cfg)
    u10, v10 = _equatorward_alongshore_wind(8.0, (lat.size, lon.size))
    calls: list[tuple[np.ndarray, np.ndarray]] = []

    def _spy(u: np.ndarray, v: np.ndarray, la: np.ndarray, **kwargs: object) -> np.ndarray:
        calls.append((np.array(u, copy=True), np.array(v, copy=True)))
        return compute_upwelling(u, v, la, **kwargs)

    day = dt.date(2020, 6, 1)
    product_id = glorys_product_for_date(day)
    nz = 5
    depth_levels = np.array([50.0, 20.0, 10.0, 5.0, 0.0])
    nj, ni = lat.size, lon.size
    thetao = np.ones((nz, nj, ni)) * 18.0
    so = np.ones((nz, nj, ni)) * 33.5
    mlotst = np.full((nj, ni), 20.0)

    with (
        patch(
            "fishai.ingestion.physics.cufes_training_covariates.compute_upwelling",
            side_effect=_spy,
        ),
        patch(
            "fishai.ingestion.physics.wcofs_glorys_grid.compute_upwelling",
            side_effect=_spy,
        ),
    ):
        glorys_fields = _compute_day_surface_fields(
            day,
            product_id,
            lat,
            lon,
            depth_levels,
            thetao,
            so,
            mlotst,
            u10,
            v10,
        )
        wcofs_fields = wcofs_covariate_arrays_on_glorys_grid(
            _synthetic_wcofs(), lat, lon, cfg, u10=u10, v10=v10
        )

    assert len(calls) == 2
    np.testing.assert_allclose(calls[0][0], calls[1][0])
    np.testing.assert_allclose(calls[0][1], calls[1][1])
    np.testing.assert_allclose(glorys_fields.upwelling, wcofs_fields["upwelling"])


def test_training_parquet_metadata_includes_upwelling_fields(tmp_path) -> None:
    lat = np.linspace(33.0, 33.1, 3)
    lon = np.linspace(-120.4, -120.3, 3)
    store = glorys_store_from_synthetic_days(
        [dt.date(2020, 1, 1)], lat=lat, lon=lon, wind_source_id="ccmp_winds"
    )
    df = __import__("pandas").DataFrame({"event_id": ["e1"], "T3m": [1.0]})
    out = tmp_path / "out.parquet"
    write_training_covariates_parquet(
        df,
        out,
        entry=require_approved("glorys", purpose="training"),
        store=store,
    )
    meta = json.loads(pq.read_table(out).schema.metadata[b"glorys"].decode())
    assert meta["upwelling_formula"] == UPWELLING_FORMULA_ID
    assert meta["upwelling_wind_source"] == "ccmp_winds"
    assert meta["upwelling_coast_angle_deg"] == PILOT_COAST_ANGLE_DEG
    assert meta["upwelling_shared_forcing"] is False
    assert meta["upwelling_status"] == "no_consistent_wind_product"
