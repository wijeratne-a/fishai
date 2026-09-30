"""Copernicus Marine GLORYS subsets for the CUFES training covariate table."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fishai.ingestion.physics.cufes_training_covariates import GlorysDayFields, GlorysSubsetBatch
from fishai.ingestion.physics.sources.glorys import (
    glorys_dataset_id_for_date,
    glorys_product_for_date,
)
from fishai.ingestion.physics.glorys_training_build import GLORYS_COVARIATE_SOURCE_COPERNICUS
from fishai.ingestion.physics.wcofs_glorys_overlap import DailyRequestBudget

# Physics join uses profiles through MLD; subset only what the table needs.
TRAINING_SUBSET_VARIABLES: tuple[str, ...] = ("thetao", "so", "mlotst")
TRAINING_SUBSET_DEPTH_MIN_M = 0.0
TRAINING_SUBSET_DEPTH_MAX_M = 200.0


def subset_nc_path(cache_dir: Path, batch: "GlorysSubsetBatch") -> Path:
    return cache_dir / (
        f"{batch.dataset_id}_{batch.date_start.isoformat()}_{batch.date_end.isoformat()}.nc"
    )


def map_days_to_subset_files(
    days: list[dt.date],
    batches: list["GlorysSubsetBatch"],
    cache_dir: Path,
) -> dict[dt.date, Path]:
    """Map each event day to the monthly subset NetCDF that contains it."""
    by_day: dict[dt.date, Path] = {}
    for batch in batches:
        path = subset_nc_path(cache_dir, batch)
        if not path.is_file():
            raise FileNotFoundError(f"missing GLORYS subset cache: {path}")
        cur = batch.date_start
        while cur <= batch.date_end:
            if cur in days:
                expected = glorys_product_for_date(cur)
                glorys_dataset_id_for_date(cur, batch.dataset_id)
                if expected != batch.dataset_id:
                    raise ValueError(
                        f"batch dataset_id {batch.dataset_id!r} does not match "
                        f"glorys_product_for_date({cur!r})"
                    )
                by_day[cur] = path
            cur += dt.timedelta(days=1)
    missing = sorted(set(days) - set(by_day))
    if missing:
        raise FileNotFoundError(f"no subset file mapped for GLORYS days: {missing[:5]}...")
    return by_day


def _coord_names(ds: xr.Dataset) -> tuple[str, str, str, str]:
    lat_name = "latitude" if "latitude" in ds.coords else "lat"
    lon_name = "longitude" if "longitude" in ds.coords else "lon"
    depth_name = "depth" if "depth" in ds.coords else "deptho"
    time_name = "time" if "time" in ds.coords else "time_counter"
    return lat_name, lon_name, depth_name, time_name


def _regrid_to_target(
    field: xr.DataArray,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    lat_name: str,
    lon_name: str,
) -> np.ndarray:
    """Nearest-neighbour onto the pilot 1/12° axes."""
    lon_axis = np.asarray(field[lon_name].values, dtype=float)
    if float(np.nanmax(lon_axis)) > 180.0:
        lon_query = np.where(lon_dst < 0, lon_dst + 360.0, lon_dst)
    else:
        lon_query = lon_dst
    out = field.interp(
        {lat_name: lat_dst, lon_name: lon_query},
        method="nearest",
    )
    return np.asarray(out.values, dtype=float)


def glorys_day_fields_from_netcdf(
    nc_path: Path,
    day: dt.date,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
) -> "GlorysDayFields":
    from fishai.ingestion.physics.cufes_training_covariates import _compute_day_surface_fields
    """Extract one calendar day from a Copernicus subset file onto the pilot grid."""
    product_id = glorys_product_for_date(day)
    glorys_dataset_id_for_date(day, product_id)
    with xr.open_dataset(nc_path) as ds:
        lat_name, lon_name, depth_name, time_name = _coord_names(ds)
        when = pd.Timestamp(day)
        slab = ds.sel({time_name: when}, method="nearest")
        if time_name in slab.coords:
            tval = pd.Timestamp(slab[time_name].values).date()
            if tval != day:
                raise ValueError(f"{nc_path}: nearest time {tval} != requested {day}")
        depth_levels = np.asarray(slab[depth_name].values, dtype=float)
        thetao = _regrid_to_target(slab["thetao"], lat_dst, lon_dst, lat_name, lon_name)
        so = _regrid_to_target(slab["so"], lat_dst, lon_dst, lat_name, lon_name)
        mlotst = _regrid_to_target(slab["mlotst"], lat_dst, lon_dst, lat_name, lon_name)
        if thetao.ndim == 2:
            thetao = thetao[np.newaxis, ...]
            so = so[np.newaxis, ...]
        if mlotst.ndim == 3:
            mlotst = mlotst[0]
    return _compute_day_surface_fields(
        day,
        product_id,
        lat_dst,
        lon_dst,
        depth_levels,
        thetao,
        so,
        mlotst,
    )


def populate_store_days_from_cache(
    store: Any,
    days: list[dt.date],
    batches: list["GlorysSubsetBatch"],
    cache_dir: Path,
) -> None:
    """Fill ``store.days`` from downloaded subset NetCDFs (one open per monthly file)."""
    day_to_path = map_days_to_subset_files(days, batches, cache_dir)
    paths = sorted(set(day_to_path.values()))
    open_ds: dict[Path, xr.Dataset] = {}
    try:
        for path in paths:
            open_ds[path] = xr.open_dataset(path)
        for day in days:
            path = day_to_path[day]
            store.days[day] = glorys_day_fields_from_open_dataset(
                open_ds[path],
                day,
                store.lat,
                store.lon,
            )
        store.covariate_data_source = GLORYS_COVARIATE_SOURCE_COPERNICUS
    finally:
        for ds in open_ds.values():
            ds.close()


def glorys_day_fields_from_open_dataset(
    ds: xr.Dataset,
    day: dt.date,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
) -> "GlorysDayFields":
    from fishai.ingestion.physics.cufes_training_covariates import _compute_day_surface_fields
    product_id = glorys_product_for_date(day)
    glorys_dataset_id_for_date(day, product_id)
    lat_name, lon_name, depth_name, time_name = _coord_names(ds)
    when = pd.Timestamp(day)
    slab = ds.sel({time_name: when}, method="nearest")
    if time_name in slab.coords:
        tval = pd.Timestamp(slab[time_name].values).date()
        if tval != day:
            raise ValueError(f"nearest time {tval} != requested {day}")
    depth_levels = np.asarray(slab[depth_name].values, dtype=float)
    thetao = _regrid_to_target(slab["thetao"], lat_dst, lon_dst, lat_name, lon_name)
    so = _regrid_to_target(slab["so"], lat_dst, lon_dst, lat_name, lon_name)
    mlotst = _regrid_to_target(slab["mlotst"], lat_dst, lon_dst, lat_name, lon_name)
    if thetao.ndim == 2:
        thetao = thetao[np.newaxis, ...]
        so = so[np.newaxis, ...]
    if mlotst.ndim == 3:
        mlotst = mlotst[0]
    return _compute_day_surface_fields(
        day,
        product_id,
        lat_dst,
        lon_dst,
        depth_levels,
        thetao,
        so,
        mlotst,
    )


def cache_byte_total(cache_dir: Path, batches: list["GlorysSubsetBatch"]) -> int:
    total = 0
    for batch in batches:
        path = subset_nc_path(cache_dir, batch)
        if path.is_file():
            total += path.stat().st_size
    return total


def product_date_coverage(
    days: list[dt.date],
) -> dict[str, dict[str, str | int]]:
    """Summarize which calendar days use each Copernicus dataset id."""
    by_product: dict[str, list[dt.date]] = {}
    for day in days:
        pid = glorys_product_for_date(day)
        by_product.setdefault(pid, []).append(day)
    out: dict[str, dict[str, str | int]] = {}
    for pid, dlist in sorted(by_product.items()):
        dlist = sorted(dlist)
        out[pid] = {
            "date_start": dlist[0].isoformat(),
            "date_end": dlist[-1].isoformat(),
            "unique_days": len(dlist),
        }
    return out


def enforce_subset_request_budget(batches: list[GlorysSubsetBatch], max_per_day: int = 200) -> None:
    budget = DailyRequestBudget(max_per_day)
    today = dt.date.today()
    for batch in batches:
        budget.charge(today, 1)
        glorys_dataset_id_for_date(batch.date_start, batch.dataset_id)
