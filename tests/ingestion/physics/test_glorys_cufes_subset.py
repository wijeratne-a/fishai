"""GLORYS subset cache → training grid (synthetic NetCDF)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from fishai.ingestion.physics.cufes_training_covariates import (
    GlorysSubsetBatch,
    plan_glorys_subset_batches,
)
from fishai.ingestion.physics.glorys_cufes_subset import (
    glorys_day_fields_from_netcdf,
    populate_store_days_from_cache,
    subset_nc_path,
)
from fishai.ingestion.physics.sources.glorys import PRODUCT_ID_MY, glorys_product_for_date
from fishai.ingestion.physics.cufes_training_covariates import glorys_store_from_synthetic_days


def _write_toy_subset(path: Path, day: dt.date) -> None:
    lat = np.linspace(33.0, 33.5, 4)
    lon = np.linspace(-120.5, -120.0, 4)
    depth = np.array([0.494, 3.0, 10.0, 50.0])
    times = np.array([np.datetime64(f"{day.isoformat()}T12:00:00")], dtype="datetime64[ns]")
    nj, ni = lat.size, lon.size
    thetao = xr.DataArray(
        15.0 + 0.01 * depth[:, None, None, None] * np.ones((depth.size, 1, nj, ni)),
        dims=("depth", "time", "latitude", "longitude"),
        coords={"depth": depth, "time": times, "latitude": lat, "longitude": lon},
    )
    so = xr.DataArray(
        33.5 + np.zeros((depth.size, 1, nj, ni)),
        dims=("depth", "time", "latitude", "longitude"),
        coords={"depth": depth, "time": times, "latitude": lat, "longitude": lon},
    )
    mlotst = xr.DataArray(
        20.0 + np.zeros((1, lat.size, lon.size)),
        dims=("time", "latitude", "longitude"),
        coords={"time": times, "latitude": lat, "longitude": lon},
    )
    ds = xr.Dataset({"thetao": thetao, "so": so, "mlotst": mlotst})
    ds.to_netcdf(path, engine="h5netcdf")


def test_subset_loader_roundtrip(tmp_path: Path) -> None:
    day = dt.date(2020, 6, 15)
    batch = GlorysSubsetBatch(
        dataset_id=glorys_product_for_date(day),
        date_start=day,
        date_end=day,
        variables=("thetao", "so", "mlotst"),
        bbox=(32.0, 35.0, -121.0, -117.0),
    )
    nc = subset_nc_path(tmp_path, batch)
    _write_toy_subset(nc, day)
    lat = np.linspace(33.0, 33.4, 5)
    lon = np.linspace(-120.4, -120.1, 5)
    fields = glorys_day_fields_from_netcdf(nc, day, lat, lon)
    assert fields.dataset_id == PRODUCT_ID_MY
    assert np.isfinite(fields.thetao).all()
    store = glorys_store_from_synthetic_days([], lat=lat, lon=lon)
    populate_store_days_from_cache(store, [day], [batch], tmp_path)
    sample = store.field_sampler(33.1, -120.2, pd.Timestamp(f"{day}T12:00:00Z"))
    assert np.isfinite(sample["T3m"])


def test_plan_batches_use_training_variables() -> None:
    batches = plan_glorys_subset_batches([dt.date(2021, 6, 30)])
    assert batches[0].variables == ("thetao", "so", "mlotst")
