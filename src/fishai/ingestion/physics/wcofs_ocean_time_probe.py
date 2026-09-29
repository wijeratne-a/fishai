"""Read WCOFS NetCDF ``ocean_time`` from public S3 with minimal byte transfer."""

from __future__ import annotations

import datetime as dt
import io
from dataclasses import dataclass
from typing import Literal

import requests
import xarray as xr

from fishai.ingestion.physics.http_util import _CONNECT_TIMEOUT, _READ_TIMEOUT
from fishai.ingestion.physics.wcofs_daily import read_ocean_time_utc
from fishai.ingestion.physics.wcofs_pds_store import (
    ListKeysFn,
    _s3_url,
    resolve_avg_nowcast_key,
    resolve_fields_key,
)
ProductKind = Literal["fields", "avg_nowcast"]
OCEAN_TIME_RANGE_BYTES = 250_000


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


def _fetch_netcdf_prefix(url: str, *, budget: HttpRequestBudget | None) -> bytes:
    headers = {"Range": f"bytes=0-{OCEAN_TIME_RANGE_BYTES - 1}"}
    if budget is not None:
        budget.charge_get()
    resp = requests.get(url, headers=headers, timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT))
    if resp.status_code not in (200, 206):
        resp.raise_for_status()
    return resp.content


def read_ocean_time_from_s3_key(key: str, *, budget: HttpRequestBudget | None = None) -> dt.datetime:
    url = _s3_url(key)
    chunk = _fetch_netcdf_prefix(url, budget=budget)
    with xr.open_dataset(io.BytesIO(chunk), engine="h5netcdf", decode_times=False) as ds:
        return read_ocean_time_utc(ds)


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
