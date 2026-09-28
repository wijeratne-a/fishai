"""Harmonize and store helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from fishai.ingestion.physics.harmonize import area_weighted_regrid, glorys_target_grid
from fishai.ingestion.physics.store import cell_id_from_indices, event_covariates_parquet, inference_parquet


def test_area_weighted_regrid_mean() -> None:
    lat_s = np.array([[33.0, 33.0], [34.0, 34.0]])
    lon_s = np.array([[-120.0, -119.5], [-120.0, -119.5]])
    field = np.array([[1.0, 3.0], [1.0, 3.0]])
    lats, lons = glorys_target_grid(32.9, 34.1, -120.1, -119.4)
    out = area_weighted_regrid(field, lat_s, lon_s, lats, lons)
    assert np.isfinite(out).any()


def test_parquet_writers_no_lat_lon_columns() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tpath = Path(tmp) / "events.parquet"
        event_covariates_parquet(
            pd.DataFrame([{"event_id": "CUFES:2020-01:SH01:1", "T3m": 1.0}]),
            tpath,
        )
        ipath = Path(tmp) / "inf.parquet"
        inference_parquet(
            [
                {
                    "cell_id": cell_id_from_indices(1, 2, 0),
                    "valid_time": "2026-01-01T00:00:00Z",
                    "source": "wcofs",
                    "qc_flags": "OK",
                    "lead_hours": 0,
                }
            ],
            ipath,
        )
        forbidden = {"lat", "lon", "latitude", "longitude"}
        for path in (tpath, ipath):
            cols = set(pd.read_parquet(path).columns)
            assert not forbidden & cols
