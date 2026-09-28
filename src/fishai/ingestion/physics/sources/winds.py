"""Wind products: CCMP daily NRT with NCEP global fallback."""

from __future__ import annotations

import io
from typing import Callable

import xarray as xr

from fishai.ingestion.physics.http_util import get_bytes
from fishai.ingestion.sources import attribution_for, require_approved

SOURCE_MODULE = "ccmp_winds"

CCMP_URL = (
    "https://coastwatch.pifsc.noaa.gov/erddap/griddap/ccmp-daily-v2-1-NRT.nc"
    "?uwnd[(last)][({la0}):1:({la1})][({lo0}):1:({lo1})]"
    "&vwnd[(last)][({la0}):1:({la1})][({lo0}):1:({lo1})]"
)
NCEP_URL = (
    "https://pae-paha.pacioos.hawaii.edu/erddap/griddap/ncep_global.nc"
    "?uwind[(last)][({la0}):1:({la1})][({lo0}):1:({lo1})]"
    "&vwind[(last)][({la0}):1:({la1})][({lo0}):1:({lo1})]"
)


def _url(template: str, bbox: tuple[float, float, float, float]) -> str:
    la0, la1, lo0, lo1 = bbox
    return template.format(la0=la0, la1=la1, lo0=lo0, lo1=lo1)


def fetch_winds(
    bbox: tuple[float, float, float, float],
    *,
    get_fn: Callable[..., bytes] | None = None,
) -> xr.Dataset:
    require_approved("ccmp_winds")
    get_fn = get_fn or get_bytes
    for template, source_id in ((CCMP_URL, "ccmp_winds"), (NCEP_URL, "ncep_winds")):
        try:
            data = get_fn(_url(template, bbox), extra_cache_key=source_id)
            engine = "h5netcdf" if data[:4] == b"\x89HDF" else "scipy"
            ds = xr.open_dataset(io.BytesIO(data), engine=engine)
            ds.attrs["attribution"] = attribution_for(source_id if source_id == "ccmp_winds" else "ncep_winds")
            ds.attrs["wind_source"] = source_id
            return ds
        except Exception:
            continue
    raise RuntimeError("wind ERDDAP fetch failed")
