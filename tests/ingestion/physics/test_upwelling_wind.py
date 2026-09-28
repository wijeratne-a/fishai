"""Coastal upwelling formula (synthetic wind only; training table leaves upwelling blank)."""

from __future__ import annotations

import datetime as dt
import math

import numpy as np
from fishai.ingestion.physics.cufes_training_covariates import (
    _compute_day_surface_fields,
    upwelling_covariate_metadata,
)
from fishai.ingestion.physics.features import (
    PILOT_COAST_ANGLE_DEG,
    PILOT_COAST_ANGLE_RAD,
    UPWELLING_FORMULA_ID,
    compute_upwelling,
)
from fishai.ingestion.physics.sources.glorys import glorys_product_for_date
from fishai.ingestion.physics.wind_shared_forcing import UPWELLING_STATUS_NO_CONSISTENT_WIND

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


def test_compute_day_surface_fields_does_not_fill_upwelling_from_glorys_inputs() -> None:
    """Training day fields must not treat GLORYS currents (or any stand-in) as 10 m wind."""
    lat = np.linspace(33.0, 33.2, 4)
    lon = np.linspace(-120.5, -120.3, 4)
    nz = 5
    depth_levels = np.array([50.0, 20.0, 10.0, 5.0, 0.0])
    nj, ni = lat.size, lon.size
    day = dt.date(2020, 6, 1)
    product_id = glorys_product_for_date(day)
    thetao = np.ones((nz, nj, ni)) * 18.0
    so = np.ones((nz, nj, ni)) * 33.5
    mlotst = np.full((nj, ni), 20.0)
    fields = _compute_day_surface_fields(
        day,
        product_id,
        lat,
        lon,
        depth_levels,
        thetao,
        so,
        mlotst,
    )
    assert np.isnan(fields.upwelling).all()


def test_upwelling_covariate_metadata_documents_no_consistent_wind() -> None:
    meta = upwelling_covariate_metadata("ccmp_winds")
    assert meta["upwelling_formula"] == UPWELLING_FORMULA_ID
    assert meta["upwelling_wind_source"] == "ccmp_winds"
    assert meta["upwelling_coast_angle_deg"] == PILOT_COAST_ANGLE_DEG
    assert meta["upwelling_shared_forcing"] is False
    assert meta["upwelling_status"] == UPWELLING_STATUS_NO_CONSISTENT_WIND
