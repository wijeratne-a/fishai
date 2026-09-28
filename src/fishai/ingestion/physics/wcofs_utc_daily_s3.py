"""
Lazy WCOFS ``fields`` reads from public S3 (pilot bbox subset) and overlap transfer counts.

Uses ``fsspec`` + ``h5netcdf``; does not download whole files when spatial indices are applied
before ``load()``.
"""

from __future__ import annotations

import datetime as dt
import json
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

import fsspec
import numpy as np
import xarray as xr

from fishai.ingestion.physics.http_util import head_ok
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, overlap_dates
from fishai.ingestion.physics.wcofs_pds_store import (
    WCOFS_PDS_BUCKET,
    ListKeysFn,
    _s3_url,
    resolve_fields_key,
)
from fishai.physics.store import CycleNotAvailable
from fishai.ingestion.physics.wcofs_utc_daily_pairing import (
    wcofs_fields_cycle_lead_for_utc_hour,
)

FIELDS_VARS_PILOT = (
    "ocean_time",
    "temp",
    "salt",
    "h",
    "zeta",
    "mask_rho",
    "lat_rho",
    "lon_rho",
    "s_rho",
    "hc",
    "Cs_r",
    "pm",
    "pn",
)


@dataclass
class TransferCounter:
    """HTTP/S3 read accounting for one overlap counting run."""

    list_requests: int = 0
    head_requests: int = 0
    get_requests: int = 0
    bytes_read: int = 0


@dataclass(frozen=True)
class HourlyFieldsFileRef:
    cycle: dt.date
    lead: str

    def as_tuple(self) -> tuple[str, str]:
        return (self.cycle.isoformat(), self.lead)


def pilot_bbox_from_config(config: dict[str, Any]) -> tuple[float, float, float, float]:
    bbox = config["pilot_bbox"]
    return (
        float(bbox["lat_min"]),
        float(bbox["lat_max"]),
        float(bbox["lon_min"]),
        float(bbox["lon_max"]),
    )


def eta_xi_slices_for_bbox(
    lat_rho: np.ndarray,
    lon_rho: np.ndarray,
    bbox: tuple[float, float, float, float],
) -> tuple[slice, slice]:
    la0, la1, lo0, lo1 = bbox
    lon = np.where(lon_rho > 180, lon_rho - 360, lon_rho)
    m = (lat_rho >= la0) & (lat_rho <= la1) & (lon >= lo0) & (lon <= lo1)
    jj, ii = np.where(m)
    if jj.size == 0:
        raise ValueError("pilot bbox does not intersect WCOFS grid")
    return slice(int(jj.min()), int(jj.max()) + 1), slice(int(ii.min()), int(ii.max()) + 1)


def unique_fields_files_for_utc_days(days: Sequence[dt.date]) -> list[HourlyFieldsFileRef]:
    seen: set[tuple[str, str]] = set()
    out: list[HourlyFieldsFileRef] = []
    for utc_day in days:
        for hour in range(24):
            cycle, lead = wcofs_fields_cycle_lead_for_utc_hour(utc_day, hour)
            key = (cycle.isoformat(), lead)
            if key in seen:
                continue
            seen.add(key)
            out.append(HourlyFieldsFileRef(cycle=cycle, lead=lead))
    return out


def _list_keys_counting(prefix: str, inner: ListKeysFn, counter: TransferCounter) -> list[str]:
    counter.list_requests += 1
    return inner(prefix)


def _tracking_list_keys(inner: ListKeysFn, counter: TransferCounter) -> ListKeysFn:
    cache: dict[str, list[str]] = {}

    def wrapped(prefix: str) -> list[str]:
        if prefix in cache:
            return cache[prefix]
        keys = _list_keys_counting(prefix, inner, counter)
        cache[prefix] = keys
        return keys

    return wrapped


class _ByteCountFile:
    def __init__(self, raw: Any, counter: TransferCounter) -> None:
        self._raw = raw
        self._counter = counter

    def read(self, size: int = -1) -> bytes:
        data = self._raw.read(size)
        self._counter.bytes_read += len(data)
        return data

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._raw.seek(offset, whence)

    def tell(self) -> int:
        return self._raw.tell()

    def close(self) -> None:
        self._raw.close()

    def __enter__(self) -> _ByteCountFile:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def head_content_length(url: str, *, counter: TransferCounter | None = None) -> int | None:
    import requests

    from fishai.ingestion.physics.http_util import _CONNECT_TIMEOUT, _READ_TIMEOUT

    if counter is not None:
        counter.head_requests += 1
    resp = requests.head(url, timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT))
    if resp.status_code != 200:
        return None
    cl = resp.headers.get("Content-Length")
    return int(cl) if cl and cl.isdigit() else None


def open_wcofs_fields_lead_pilot_subset(
    cycle: dt.date,
    lead: str,
    bbox: tuple[float, float, float, float],
    *,
    list_keys: ListKeysFn | None = None,
    counter: TransferCounter | None = None,
) -> xr.Dataset:
    """
    Open one WCOFS fields lead from S3, subset to the pilot bbox, load only that subset.
    """
    if list_keys is None:
        from fishai.ingestion.physics.wcofs_pds_s3_list import list_keys_under_prefix

        list_keys = list_keys_under_prefix
    if counter is not None:
        list_keys = _tracking_list_keys(list_keys, counter)

    key = resolve_fields_key(cycle, lead, list_keys)
    url = f"s3://{WCOFS_PDS_BUCKET}/{key.lstrip('/')}"
    fs = fsspec.filesystem("s3", anon=True)
    if counter is not None:
        counter.get_requests += 1
        raw = fs.open(url, "rb")
        handle: Any = _ByteCountFile(raw, counter)
    else:
        handle = fs.open(url, "rb")

    with handle as f:
        ds_full = xr.open_dataset(f, engine="h5netcdf", decode_times=False)
        lat = np.asarray(ds_full["lat_rho"].values, dtype=float)
        lon = np.asarray(ds_full["lon_rho"].values, dtype=float)
        js, ie = eta_xi_slices_for_bbox(lat, lon, bbox)
        present = [v for v in FIELDS_VARS_PILOT if v in ds_full.variables or v in ds_full.dims]
        sub = ds_full[present].isel(eta_rho=js, xi_rho=ie)
        out = sub.load()
        out.attrs.setdefault("wcofs_s3_key", key)
        out.attrs.setdefault("cycle", f"{cycle.strftime('%Y%m%d')}T03Z")
        out.attrs.setdefault("wcofs_pilot_eta_xi_slice", f"{js.start}:{js.stop},{ie.start}:{ie.stop}")
    return out


@dataclass
class HourlyUtcMeanOverlapCountReport:
    overlap_days: int
    unique_fields_files: int
    pairing_opens_per_overlap_window: int
    list_requests: int
    head_requests: int
    resolved_fields_files: int
    total_object_bytes_head: int | None
    s3_reachable: bool
    sample_lazy_bytes_read: int | None = None
    sample_lazy_get_requests: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "overlap_days": self.overlap_days,
            "unique_fields_files": self.unique_fields_files,
            "pairing_opens_per_overlap_window": self.pairing_opens_per_overlap_window,
            "list_requests": self.list_requests,
            "head_requests": self.head_requests,
            "resolved_fields_files": self.resolved_fields_files,
            "total_object_bytes_head": self.total_object_bytes_head,
            "s3_reachable": self.s3_reachable,
            "sample_lazy_bytes_read": self.sample_lazy_bytes_read,
            "sample_lazy_get_requests": self.sample_lazy_get_requests,
        }


def count_hourly_utc_mean_overlap_transfer(
    config: dict[str, Any] | None = None,
    *,
    days: Sequence[dt.date] | None = None,
    run_lazy_sample: bool = True,
) -> HourlyUtcMeanOverlapCountReport:
    """
    Count unique files and HTTP requests for the configured overlap window.

    When WCOFS S3 is reachable, issues real LIST/HEAD (and one lazy subset GET sample).
    """
    config = config or load_overlap_config()
    days = list(days) if days is not None else overlap_dates(config)
    refs = unique_fields_files_for_utc_days(days)
    counter = TransferCounter()
    from fishai.ingestion.physics.wcofs_pds_s3_list import list_keys_under_prefix

    list_keys = _tracking_list_keys(list_keys_under_prefix, counter)
    s3_reachable = False
    sample_ref: HourlyFieldsFileRef | None = None
    for ref in reversed(refs):
        try:
            probe_key = resolve_fields_key(ref.cycle, ref.lead, list_keys)
        except (CycleNotAvailable, OSError):
            continue
        try:
            reachable = head_ok(_s3_url(probe_key))
        except OSError:
            reachable = False
        if reachable:
            s3_reachable = True
            sample_ref = ref
            break

    total_bytes: int | None = None
    sample_lazy_bytes: int | None = None
    sample_lazy_gets: int | None = None
    resolved_count = 0

    if s3_reachable:
        total_bytes = 0
        head_counter = TransferCounter()
        resolved_keys: list[str] = []
        for ref in refs:
            try:
                key = resolve_fields_key(ref.cycle, ref.lead, list_keys)
            except CycleNotAvailable:
                continue
            resolved_keys.append(key)
        resolved_count = len(resolved_keys)
        for key in resolved_keys:
            try:
                cl = head_content_length(_s3_url(key), counter=head_counter)
            except OSError:
                continue
            if cl is not None:
                total_bytes += cl
        counter.head_requests = head_counter.head_requests

        if run_lazy_sample and sample_ref is not None:
            lazy_counter = TransferCounter()
            bbox = pilot_bbox_from_config(config)
            try:
                open_wcofs_fields_lead_pilot_subset(
                    sample_ref.cycle,
                    sample_ref.lead,
                    bbox,
                    list_keys=list_keys,
                    counter=lazy_counter,
                )
                sample_lazy_bytes = lazy_counter.bytes_read
                sample_lazy_gets = lazy_counter.get_requests
            except Exception:
                sample_lazy_bytes = None
                sample_lazy_gets = None

    return HourlyUtcMeanOverlapCountReport(
        overlap_days=len(days),
        unique_fields_files=len(refs),
        pairing_opens_per_overlap_window=24 * len(days),
        list_requests=counter.list_requests,
        head_requests=counter.head_requests,
        resolved_fields_files=resolved_count,
        total_object_bytes_head=total_bytes,
        s3_reachable=s3_reachable,
        sample_lazy_bytes_read=sample_lazy_bytes,
        sample_lazy_get_requests=sample_lazy_gets,
    )


def main_count_overlap(argv: Iterable[str] | None = None) -> int:
    report = count_hourly_utc_mean_overlap_transfer()
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main_count_overlap())
