"""Helpers for CUFES training covariate integration tests (not production)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from fishai.ingestion.physics.cufes_training_covariates import (
    GlorysSubsetBatch,
    GlorysFieldStore,
    new_glorys_field_store_for_live_build,
)
from fishai.ingestion.physics.glorys_cufes_subset import populate_store_days_from_cache, subset_nc_path
from fishai.ingestion.physics.sources.glorys import glorys_product_for_date
from fishai.ingestion.physics.wcofs_h_glorys_store import export_wcofs_h_glorys_grid
from test_wcofs_h_glorys_store import _mini_wcofs

import numpy as np
import xarray as xr


def write_toy_glorys_subset_nc(
    path: Path,
    day: dt.date,
    *,
    lat: np.ndarray | None = None,
    lon: np.ndarray | None = None,
) -> None:
    if lat is None:
        lat = np.linspace(33.0, 33.5, 4)
    if lon is None:
        lon = np.linspace(-120.5, -120.0, 4)
    depth = np.array([50.0, 20.0, 10.0, 5.0, 0.494])
    times = np.array([np.datetime64(f"{day.isoformat()}T12:00:00")], dtype="datetime64[ns]")
    nj, ni = lat.size, lon.size
    base_temp = np.array([10.0, 15.0, 17.8, 17.9, 18.0])
    thetao = xr.DataArray(
        base_temp[:, None, None, None] * np.ones((depth.size, 1, nj, ni)),
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


def live_store_with_wcofs_h_and_glorys_days(
    tmp_path: Path,
    days: list[dt.date],
) -> GlorysFieldStore:
    """WCOFS ``h``/``hmin`` from a ROMS-like grid file plus toy Copernicus subset NetCDFs."""
    artifact = tmp_path / "wcofs_h_glorys_pilot.zarr"
    manifest = tmp_path / "wcofs_h_glorys_grid.json"
    export_wcofs_h_glorys_grid(
        _mini_wcofs(h_value=95.0, hmin_attr=8.0),
        source_file="tests/wcofs_roms_sample.nc",
        artifact_path=artifact,
        manifest_path=manifest,
    )
    store = new_glorys_field_store_for_live_build(
        manifest_path=manifest,
        artifact_path=artifact,
    )
    batches: list[GlorysSubsetBatch] = []
    for day in days:
        batches.append(
            GlorysSubsetBatch(
                dataset_id=glorys_product_for_date(day),
                date_start=day,
                date_end=day,
                variables=("thetao", "so", "mlotst"),
                bbox=(32.0, 35.0, -121.0, -117.0),
            )
        )
        nc = subset_nc_path(tmp_path / "glorys_cache", batches[-1])
        nc.parent.mkdir(parents=True, exist_ok=True)
        write_toy_glorys_subset_nc(nc, day, lat=store.lat, lon=store.lon)
    populate_store_days_from_cache(store, days, batches, tmp_path / "glorys_cache")
    return store
