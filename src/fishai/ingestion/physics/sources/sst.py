"""ERDDAP SST sources: MUR L4 then NOAA blended day+night."""

from __future__ import annotations

import io
from typing import Callable

import xarray as xr

from fishai.ingestion.physics.http_util import get_bytes
from fishai.ingestion.sources import attribution_for, require_approved

SOURCE_MODULE = "mur_sst"

MUR_URL = (
    "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.nc"
    "?analysed_sst[(last)][({la0}):1:({la1})][({lo0}):1:({lo1})]"
)
BLENDED_URL = (
    "https://coastwatch.pfeg.noaa.gov/erddap/griddap/noaacwBLENDEDsstDNDaily.nc"
    "?sst[(last)][({la0}):1:({la1})][({lo0}):1:({lo1})]"
)


def _erddap_bbox_url(template: str, bbox: tuple[float, float, float, float]) -> str:
    la0, la1, lo0, lo1 = bbox
    return template.format(la0=la0, la1=la1, lo0=lo0, lo1=lo1)


def fetch_sst(
    bbox: tuple[float, float, float, float],
    *,
    get_fn: Callable[..., bytes] | None = None,
) -> xr.Dataset:
    """Try jplMURSST41, then noaacwBLENDEDsstDNDaily."""
    require_approved("mur_sst")
    get_fn = get_fn or get_bytes
    urls = [_erddap_bbox_url(MUR_URL, bbox), _erddap_bbox_url(BLENDED_URL, bbox)]
    last_err: Exception | None = None
    for url in urls:
        try:
            data = get_fn(url, extra_cache_key=str(bbox))
            engine = "h5netcdf" if data[:4] == b"\x89HDF" else "scipy"
            ds = xr.open_dataset(io.BytesIO(data), engine=engine)
            ds.attrs["attribution"] = attribution_for("mur_sst")
            return ds
        except Exception as exc:  # noqa: BLE001
            last_err = exc
    raise RuntimeError("SST ERDDAP fetch failed") from last_err
