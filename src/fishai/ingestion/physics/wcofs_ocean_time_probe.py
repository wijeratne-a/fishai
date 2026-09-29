"""Read WCOFS NetCDF ``ocean_time`` from public S3 with minimal byte transfer."""

from __future__ import annotations

import datetime as dt
import io
from dataclasses import dataclass
from typing import Literal

import fsspec
import xarray as xr

from fishai.ingestion.physics.http_util import get_bytes
from fishai.ingestion.physics.wcofs_daily import read_ocean_time_utc
from fishai.ingestion.physics.wcofs_pds_store import (
    WCOFS_PDS_BUCKET,
    ListKeysFn,
    _s3_url,
    resolve_avg_nowcast_key,
    resolve_fields_key,
)

ProductKind = Literal["fields", "avg_nowcast"]


@dataclass
class HttpRequestBudget:
    list_requests: int = 0
    get_requests: int = 0

    def charge_list(self, n: int = 1) -> None:
        self.list_requests += n

    def charge_get(self, n: int = 1) -> None:
        self.get_requests += n

    @property
    def total(self) -> int:
        return self.list_requests + self.get_requests


_list_cache: dict[str, list[str]] = {}


def _cached_list_keys(inner: ListKeysFn, budget: HttpRequestBudget | None) -> ListKeysFn:
    def wrapped(prefix: str) -> list[str]:
        if prefix in _list_cache:
            return _list_cache[prefix]
        if budget is not None:
            budget.charge_list()
        keys = inner(prefix)
        _list_cache[prefix] = keys
        return keys

    return wrapped


def _read_ocean_time_from_open_dataset(open_fn) -> dt.datetime:
    with open_fn() as handle:
        ds = xr.open_dataset(handle, engine="h5netcdf", decode_times=False)
        try:
            ds["ocean_time"].load()
            return read_ocean_time_utc(ds)
        finally:
            ds.close()


def read_ocean_time_from_s3_key(key: str, *, budget: HttpRequestBudget | None = None) -> dt.datetime:
    """Lazy S3 read of ``ocean_time`` only (HDF5 metadata + one scalar chunk)."""
    url = f"s3://{WCOFS_PDS_BUCKET}/{key.lstrip('/')}"
    fs = fsspec.filesystem("s3", anon=True)

    def open_s3():
        if budget is not None:
            budget.charge_get()
        return fs.open(url, "rb")

    try:
        return _read_ocean_time_from_open_dataset(open_s3)
    except Exception:
        if budget is not None:
            budget.charge_get()
        data = get_bytes(_s3_url(key), extra_cache_key=key)
        return _read_ocean_time_from_open_dataset(lambda: io.BytesIO(data))


def probe_fields_ocean_time(
    cycle: dt.date,
    lead: str,
    list_keys: ListKeysFn,
    *,
    budget: HttpRequestBudget | None = None,
) -> tuple[dt.datetime, str]:
    key = resolve_fields_key(cycle, lead, list_keys)
    return read_ocean_time_from_s3_key(key, budget=budget), key


def probe_avg_nowcast_ocean_time(
    cycle: dt.date,
    list_keys: ListKeysFn,
    *,
    budget: HttpRequestBudget | None = None,
) -> tuple[dt.datetime, str]:
    key = resolve_avg_nowcast_key(cycle, list_keys)
    return read_ocean_time_from_s3_key(key, budget=budget), key


def wrap_list_keys(inner: ListKeysFn, budget: HttpRequestBudget | None) -> ListKeysFn:
    return _cached_list_keys(inner, budget)
