"""GLORYS subset cache → training grid (synthetic NetCDF)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
from fishai.ingestion.physics.cufes_training_covariates import (
    GlorysSubsetBatch,
    plan_glorys_subset_batches,
)
from fishai.ingestion.physics.glorys_cufes_subset import (
    glorys_day_fields_from_netcdf,
    subset_nc_path,
)
from fishai.ingestion.physics.sources.glorys import PRODUCT_ID_MY, glorys_product_for_date
from fishai.ingestion.physics.glorys_training_build import GLORYS_COVARIATE_SOURCE_COPERNICUS
from cufes_training_test_helpers import live_store_with_wcofs_h_and_glorys_days, write_toy_glorys_subset_nc


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
    write_toy_glorys_subset_nc(nc, day)
    lat = np.linspace(33.0, 33.4, 5)
    lon = np.linspace(-120.4, -120.1, 5)
    fields = glorys_day_fields_from_netcdf(nc, day, lat, lon)
    assert fields.dataset_id == PRODUCT_ID_MY
    assert np.isfinite(fields.thetao).all()
    store = live_store_with_wcofs_h_and_glorys_days(tmp_path, [day])
    assert store.covariate_data_source == GLORYS_COVARIATE_SOURCE_COPERNICUS
    sample = store.field_sampler(float(store.lat[1]), float(store.lon[1]), pd.Timestamp(f"{day}T12:00:00Z"))
    assert np.isfinite(sample["T3m"])


def test_plan_batches_use_training_variables() -> None:
    batches = plan_glorys_subset_batches([dt.date(2021, 6, 30)])
    assert batches[0].variables == ("thetao", "so", "mlotst")
