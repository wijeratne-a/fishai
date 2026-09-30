"""
Wind products for upwelling (CCMP V2.1 NRT ERDDAP).

Training/hindcast uses CCMP only (no product mixing). Operational ``fetch_winds`` may
fall back to PacIOOS NCEP GFS when CCMP is unavailable; that path is **not** qualified
for ``upwelling_shared_forcing`` (see ``wind_shared_forcing.py``).
"""

from __future__ import annotations

import datetime as dt
import io
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr

from fishai.ingestion.physics.http_util import get_bytes
from fishai.ingestion.physics.wcofs_glorys_overlap import DailyRequestBudget, DailyRequestBudgetExceeded
from fishai.ingestion.physics.wind_pull_log import append_wind_pull_log, build_wind_pull_record
from fishai.ingestion.physics.wind_shared_forcing import (
    CCMP_NRT_ERDDAP_ID,
    require_day_within_ccmp_nrt,
)
from fishai.ingestion.sources import REPO_ROOT, attribution_for, get_source_entry, require_approved

SOURCE_MODULE = "ccmp_winds"

CCMP_DATASET_ID = CCMP_NRT_ERDDAP_ID
NCEP_DATASET_ID = "ncep_global"
WIND_VARIABLES = ("uwnd", "vwnd")

CCMP_LAST_URL = (
    "https://coastwatch.pifsc.noaa.gov/erddap/griddap/ccmp-daily-v2-1-NRT.nc"
    "?uwnd[(last)][({la0}):1:({la1})][({lo0}):1:({lo1})]"
    "&vwnd[(last)][({la0}):1:({la1})][({lo0}):1:({lo1})]"
)
NCEP_LAST_URL = (
    "https://pae-paha.pacioos.hawaii.edu/erddap/griddap/ncep_global.nc"
    "?uwind[(last)][({la0}):1:({la1})][({lo0}):1:({lo1})]"
    "&vwind[(last)][({la0}):1:({la1})][({lo0}):1:({lo1})]"
)


def _pull_log_path(source_id: str) -> Path:
    entry = get_source_entry(source_id)
    rel = entry.get("pull_log_path") or "data/provenance/wind_pull_log.jsonl"
    path = Path(rel)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _url(template: str, bbox: tuple[float, float, float, float], *, time_sel: str) -> str:
    la0, la1, lo0, lo1 = bbox
    return template.format(la0=la0, la1=la1, lo0=lo0, lo1=lo1, time=time_sel)


CCMP_DAY_URL = (
    "https://coastwatch.pifsc.noaa.gov/erddap/griddap/ccmp-daily-v2-1-NRT.nc"
    "?uwnd[({time}):1:({time})][({la0}):1:({la1})][({lo0}):1:({lo1})]"
    "&vwnd[({time}):1:({time})][({la0}):1:({la1})][({lo0}):1:({lo1})]"
)
NCEP_DAY_URL = (
    "https://pae-paha.pacioos.hawaii.edu/erddap/griddap/ncep_global.nc"
    "?uwind[({time}):1:({time})][({la0}):1:({la1})][({lo0}):1:({lo1})]"
    "&vwind[({time}):1:({time})][({la0}):1:({la1})][({lo0}):1:({lo1})]"
)


def _dataset_version(ds: xr.Dataset, dataset_id: str) -> str:
    for key in ("version", "product_version", "history", "dataset_version"):
        if key in ds.attrs and ds.attrs[key]:
            return str(ds.attrs[key])[:200]
    return dataset_id


def _open_erddap_bytes(data: bytes) -> xr.Dataset:
    engine = "h5netcdf" if data[:4] == b"\x89HDF" else "scipy"
    return xr.open_dataset(io.BytesIO(data), engine=engine)


def _normalize_wind_dataset(ds: xr.Dataset, source_id: str) -> xr.Dataset:
    if "uwnd" in ds:
        u_name, v_name = "uwnd", "vwnd"
    else:
        u_name, v_name = "uwind", "vwind"
    ds = ds.rename({u_name: "u10", v_name: "v10"})
    ds.attrs["attribution"] = attribution_for(
        "ccmp_winds" if source_id == "ccmp_winds" else "ncep_winds"
    )
    ds.attrs["wind_source"] = source_id
    ds.attrs["wind_dataset_id"] = CCMP_DATASET_ID if source_id == "ccmp_winds" else NCEP_DATASET_ID
    return ds


def fetch_winds(
    bbox: tuple[float, float, float, float],
    *,
    get_fn: Callable[..., bytes] | None = None,
) -> xr.Dataset:
    """Latest-available daily winds (nowcast / inference)."""
    require_approved("ccmp_winds")
    get_fn = get_fn or get_bytes
    for template, source_id in ((CCMP_LAST_URL, "ccmp_winds"), (NCEP_LAST_URL, "ncep_winds")):
        try:
            data = get_fn(_url(template, bbox, time_sel="last"), extra_cache_key=source_id)
            ds = _normalize_wind_dataset(_open_erddap_bytes(data), source_id)
            return ds
        except Exception:
            continue
    raise RuntimeError("wind ERDDAP fetch failed")


def fetch_winds_for_day(
    day: dt.date,
    bbox: tuple[float, float, float, float],
    *,
    purpose: str = "training",
    get_fn: Callable[..., bytes] | None = None,
    log_path: Path | None = None,
    budget: DailyRequestBudget | None = None,
) -> xr.Dataset:
    """
    Historical daily 10 m winds for ``day`` (training / hindcast only).

    Uses only the approved CCMP V2.1 NRT ERDDAP stream (no alternate product fallback).
    Appends one pull-log line per successful request.
    """
    require_approved("ccmp_winds", purpose=purpose)
    require_day_within_ccmp_nrt(day)
    get_fn = get_fn or get_bytes
    time_sel = f"{day.isoformat()}T12:00:00Z"
    if budget is not None:
        budget.charge(day, 1)
    try:
        url = _url(CCMP_DAY_URL, bbox, time_sel=time_sel)
        data = get_fn(url, extra_cache_key=f"ccmp_winds:{day.isoformat()}")
        ds = _normalize_wind_dataset(_open_erddap_bytes(data), "ccmp_winds")
        version = _dataset_version(ds, CCMP_DATASET_ID)
        append_wind_pull_log(
            build_wind_pull_record(
                dataset_id=CCMP_DATASET_ID,
                date_start=day.isoformat(),
                date_end=day.isoformat(),
                variables=WIND_VARIABLES,
                bbox=bbox,
                dataset_version=version,
            ),
            log_path=log_path or _pull_log_path("ccmp_winds"),
        )
        return ds
    except DailyRequestBudgetExceeded:
        raise
    except Exception as exc:
        raise RuntimeError(f"wind ERDDAP fetch failed for {day.isoformat()}") from exc


def fetch_winds_date_range(
    start: dt.date,
    end: dt.date,
    bbox: tuple[float, float, float, float],
    *,
    purpose: str = "training",
    get_fn: Callable[..., bytes] | None = None,
    max_requests_per_day: int = 200,
    log_path: Path | None = None,
) -> dict[dt.date, xr.Dataset]:
    """Fetch one ERDDAP subset per day in ``[start, end]`` (inclusive)."""
    budget = DailyRequestBudget(max_requests_per_day)
    out: dict[dt.date, xr.Dataset] = {}
    cur = start
    while cur <= end:
        out[cur] = fetch_winds_for_day(
            cur,
            bbox,
            purpose=purpose,
            get_fn=get_fn,
            log_path=log_path,
            budget=budget,
        )
        cur += dt.timedelta(days=1)
    return out


def wind_to_glorys_grid(
    ds_wind: xr.Dataset,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Nearest-neighbour 10 m winds onto a regular lat/lon grid."""
    u = ds_wind["u10"]
    v = ds_wind["v10"]
    if "time" in u.dims:
        u = u.isel(time=0)
        v = v.isel(time=0)
    lat_src = np.asarray(u.lat.values if "lat" in u.coords else u.latitude.values, dtype=float)
    lon_src = np.asarray(u.lon.values if "lon" in u.coords else u.longitude.values, dtype=float)
    u2d = np.asarray(u.values, dtype=float)
    v2d = np.asarray(v.values, dtype=float)
    if u2d.ndim > 2:
        u2d = u2d.reshape(u2d.shape[-2], u2d.shape[-1])
        v2d = v2d.reshape(v2d.shape[-2], v2d.shape[-1])
    nj, ni = lat_dst.size, lon_dst.size
    u_out = np.full((nj, ni), np.nan, dtype=float)
    v_out = np.full((nj, ni), np.nan, dtype=float)
    for j, la in enumerate(lat_dst):
        for i, lo in enumerate(lon_dst):
            j0 = int(np.argmin(np.abs(lat_src - la)))
            i0 = int(np.argmin(np.abs(lon_src - lo)))
            u_out[j, i] = u2d[j0, i0]
            v_out[j, i] = v2d[j0, i0]
    return u_out, v_out


def wind_grids_for_days(
    days: Sequence[dt.date],
    lat: np.ndarray,
    lon: np.ndarray,
    bbox: tuple[float, float, float, float],
    *,
    purpose: str = "training",
    get_fn: Callable[..., bytes] | None = None,
    log_path: Path | None = None,
) -> tuple[dict[dt.date, tuple[np.ndarray, np.ndarray]], str]:
    """
    Fetch (or mock) daily 10 m winds and regrid onto ``lat`` × ``lon``.

    Returns per-day ``(u10, v10)`` arrays and the wind source id from the last fetch.
    """
    if not days:
        return {}, "ccmp_winds"
    ordered = sorted(days)
    wind_by_day = fetch_winds_date_range(
        ordered[0],
        ordered[-1],
        bbox,
        purpose=purpose,
        get_fn=get_fn,
        log_path=log_path,
    )
    out: dict[dt.date, tuple[np.ndarray, np.ndarray]] = {}
    source_id = "ccmp_winds"
    for day in ordered:
        ds = wind_by_day[day]
        source_id = str(ds.attrs.get("wind_source", source_id))
        out[day] = wind_to_glorys_grid(ds, lat, lon)
    return out, source_id
