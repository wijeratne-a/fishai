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
from fishai.ingestion.physics.sources.winds import CCMP_DATASET_ID, fetch_winds_for_day
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    glorys_grid_from_config,
    load_overlap_config,
    wcofs_covariate_arrays_on_glorys_grid,
)
from fishai.ingestion.sources import require_approved
from tests.ingestion.physics.test_wcofs_covariate_grid_parity import _synthetic_wcofs


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


def test_fetch_winds_for_day_mock_appends_pull_log(tmp_path) -> None:
    lat = np.linspace(33.0, 34.0, 3)
    lon = np.linspace(-121.0, -120.0, 3)
    u = np.ones((1, lat.size, lon.size)) * 5.0
    v = np.zeros((1, lat.size, lon.size))
    payload = xr.Dataset(
        {
            "uwnd": (("time", "lat", "lon"), u),
            "vwnd": (("time", "lat", "lon"), v),
        },
        attrs={"version": "ccmp-test-v1"},
    )
    buf = payload.to_netcdf()

    def get_fn(url: str, **kwargs: object) -> bytes:
        return buf

    log_path = tmp_path / "wind.jsonl"
    day = dt.date(2019, 5, 1)
    bbox = (32.0, 35.0, -121.0, -117.0)
    ds = fetch_winds_for_day(day, bbox, purpose="training", get_fn=get_fn, log_path=log_path)
    assert ds.attrs["wind_source"] == "ccmp_winds"
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = __import__("json").loads(lines[0])
    assert record["dataset_id"] == CCMP_DATASET_ID
    assert record["dataset_version"] == "ccmp-test-v1"


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
