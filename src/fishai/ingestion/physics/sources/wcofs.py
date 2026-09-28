"""NOAA WCOFS fields from public S3 with CO-OPS THREDDS OPeNDAP fallback."""

from __future__ import annotations

import datetime as dt
import io
from typing import Any, Callable, Sequence

import numpy as np
import xarray as xr

from fishai.ingestion.physics.http_util import get_bytes, head_ok
from fishai.ingestion.physics.vertical import bottom_layer, mld, s_to_z, thermocline_depth
from fishai.ingestion.sources import attribution_for, require_approved

SOURCE_MODULE = "wcofs"

S3_BASE = "https://noaa-nos-ofs-pds.s3.amazonaws.com/wcofs/netcdf"
THREDDS_BASE = "https://opendap.co-ops.nos.noaa.gov/thredds/dodsC/NOAA/WCOFS/MODELS"

NOWCAST_LEADS = tuple(f"n{k:03d}" for k in range(3, 25, 3))
FORECAST_LEADS = tuple(f"f{k:03d}" for k in range(3, 73, 3))
ALL_FIELD_LEADS = NOWCAST_LEADS + FORECAST_LEADS
CYCLE_PROBE_LEAD = "n024"
DEFAULT_SUBSET_MARGIN_CELLS = 2

# Target timeline: hours from requested run time R (03Z) at 3-hourly steps.
TARGET_VALID_OFFSETS_H = tuple(list(range(-21, 1, 3)) + list(range(3, 73, 3)))


def cycle_run_time(cycle_date: dt.date) -> dt.datetime:
    return dt.datetime.combine(cycle_date, dt.time(3, 0), tzinfo=dt.timezone.utc)


def valid_time_for_lead_tag(cycle_date: dt.date, lead_tag: str) -> dt.datetime:
    """WCOFS fields valid time: nNNN at R-(24-NNN), fNNN at R+NNN."""
    r = cycle_run_time(cycle_date)
    suffix = int(lead_tag[1:])
    if lead_tag.startswith("n"):
        return r - dt.timedelta(hours=24 - suffix)
    return r + dt.timedelta(hours=suffix)


def valid_time_offset_from_r(cycle_date: dt.date, lead_tag: str, *, requested: dt.date) -> int:
    valid = valid_time_for_lead_tag(cycle_date, lead_tag)
    r_req = cycle_run_time(requested)
    return int((valid - r_req).total_seconds() // 3600)


def lead_tag_for_valid_offset(hours_from_requested_r: int) -> str:
    if hours_from_requested_r <= 0:
        n = 24 + hours_from_requested_r
        tag = f"n{n:03d}"
        if tag not in NOWCAST_LEADS:
            raise ValueError(f"invalid nowcast offset {hours_from_requested_r}")
        return tag
    tag = f"f{hours_from_requested_r:03d}"
    if tag not in FORECAST_LEADS:
        raise ValueError(f"invalid forecast offset {hours_from_requested_r}")
    return tag


def lead_tag_for_age_from_source(age_hours: int) -> str:
    """Map hours from a source cycle's R to the fields lead tag covering that valid time."""
    if age_hours <= 0:
        tag = f"n{24 + age_hours:03d}"
        if tag not in NOWCAST_LEADS:
            raise ValueError(f"age {age_hours} outside nowcast range")
        return tag
    tag = f"f{age_hours:03d}"
    if tag not in FORECAST_LEADS:
        raise ValueError(f"age {age_hours} outside forecast range")
    return tag


def operational_lead_tags() -> tuple[str, ...]:
    return ALL_FIELD_LEADS


def lead_hour_from_tag(lead: str) -> int:
    return int(lead[1:])


def lead_tag_for_hour(hour: int) -> str:
    """Legacy helper: hour is forecast age from source R (nowcast hours map to n*, else f*)."""
    return lead_tag_for_age_from_source(hour)


def fields_s3_key(day: dt.date, lead: str) -> str:
    ymd = day.strftime("%Y%m%d")
    return f"wcofs/netcdf/{day:%Y/%m/%d}/wcofs.t03z.{ymd}.fields.{lead}.nc"


def _fields_url_s3(day: dt.date, lead: str) -> str:
    return f"{S3_BASE}/{fields_s3_key(day, lead)}"


def _fields_url_thredds(day: dt.date, lead: str) -> str:
    ymd = day.strftime("%Y%m%d")
    return f"{THREDDS_BASE}/{day:%Y/%m/%d}/wcofs.t03z.{ymd}.fields.{lead}.nc"


def cycle_available(
    date: dt.date,
    *,
    head_fn: Callable[[str], bool] | None = None,
) -> bool:
    """Return True if the 03z cycle ``fields.n024`` is reachable on S3."""
    require_approved("wcofs")
    check = head_fn or head_ok
    return check(_fields_url_s3(date, CYCLE_PROBE_LEAD))


def subset_bbox(
    ds: xr.Dataset,
    bbox: tuple[float, float, float, float],
    *,
    margin_cells: int = DEFAULT_SUBSET_MARGIN_CELLS,
) -> xr.Dataset:
    """Subset to pilot bbox on rho grid, expanding indices by ``margin_cells``."""
    return _subset_bbox(ds, bbox, margin_cells=margin_cells)


def _subset_bbox(
    ds: xr.Dataset,
    bbox: tuple[float, float, float, float],
    *,
    margin_cells: int = 0,
) -> xr.Dataset:
    la0, la1, lo0, lo1 = bbox
    lat = ds.lat_rho.values
    lon = ds.lon_rho.values
    lon = np.where(lon > 180, lon - 360, lon)
    m = (lat >= la0) & (lat <= la1) & (lon >= lo0) & (lon <= lo1)
    jj, ii = np.where(m)
    if jj.size == 0:
        raise ValueError("bbox does not intersect WCOFS grid")
    j0, j1 = int(jj.min()), int(jj.max()) + 1
    i0, i1 = int(ii.min()), int(ii.max()) + 1
    if margin_cells:
        j0 = max(0, j0 - margin_cells)
        i0 = max(0, i0 - margin_cells)
        j1 = min(ds.sizes["eta_rho"], j1 + margin_cells)
        i1 = min(ds.sizes["xi_rho"], i1 + margin_cells)
    return ds.isel(eta_rho=slice(j0, j1), xi_rho=slice(i0, i1))


def _open_dataset_from_bytes(data: bytes) -> xr.Dataset:
    return xr.open_dataset(io.BytesIO(data), engine="h5netcdf", decode_times=False)


open_dataset_from_bytes = _open_dataset_from_bytes


def _fetch_one(
    day: dt.date,
    lead: str,
    bbox: tuple[float, float, float, float],
    *,
    get_fn: Callable[..., bytes] | None = None,
    prefer_s3: bool = True,
) -> xr.Dataset:
    get_fn = get_fn or get_bytes
    urls = [_fields_url_s3(day, lead), _fields_url_thredds(day, lead)]
    if not prefer_s3:
        urls = list(reversed(urls))
    last_err: Exception | None = None
    for url in urls:
        try:
            data = get_fn(url, extra_cache_key=f"{day.isoformat()}_{lead}")
            ds = _open_dataset_from_bytes(data)
            return _subset_bbox(ds, bbox, margin_cells=DEFAULT_SUBSET_MARGIN_CELLS)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
    raise RuntimeError(f"WCOFS fetch failed for {day} {lead}") from last_err


def fetch_cycle(
    date: dt.date,
    leads: Sequence[str],
    bbox: tuple[float, float, float, float],
    *,
    get_fn: Callable[..., bytes] | None = None,
    head_fn: Callable[[str], bool] | None = None,
) -> xr.Dataset:
    """
    Fetch and merge WCOFS ``fields`` subsets for the pilot bbox.

    Returns an xarray Dataset with per-lead variables and derived bottom/MLD fields
    for the first lead.
    """
    entry = require_approved("wcofs")
    if not cycle_available(date, head_fn=head_fn):
        raise FileNotFoundError(f"WCOFS cycle not available for {date}")

    datasets: list[xr.Dataset] = []
    ref_raw: xr.Dataset | None = None
    for lead in leads:
        sub = _fetch_one(date, lead, bbox, get_fn=get_fn)
        if ref_raw is None:
            ref_raw = sub
        lh = int(lead[1:])
        sub = sub.expand_dims(lead_hours=[lh])
        datasets.append(sub)

    merged = xr.concat(datasets, dim="lead_hours")
    merged.attrs["attribution"] = attribution_for("wcofs")
    merged.attrs["source"] = "wcofs"
    merged.attrs["cycle"] = f"{date.strftime('%Y%m%d')}T03Z"

    # Derive depth diagnostics on first lead
    ref = ref_raw
    assert ref is not None

    def _surface(da: xr.DataArray) -> xr.DataArray:
        return da.isel(ocean_time=0) if "ocean_time" in da.dims else da

    h = ref.h.values
    zeta = _surface(ref.zeta).values
    temp = _surface(ref.temp).values
    salt = _surface(ref.salt).values
    s_rho = ref.s_rho.values
    hc = float(ref.hc.values)
    cs_r = ref.Cs_r.values if "Cs_r" in ref else None
    z = s_to_z(h, zeta, s_rho, hc, cs_r=cs_r)
    wet = ref.mask_rho.values == 1
    feats: dict[str, Any] = bottom_layer(temp, salt)
    feats["mld_m"] = np.where(wet, mld(z, temp), np.nan)
    feats["thermocline_depth_m"] = np.where(wet, thermocline_depth(z, temp), np.nan)
    for name, arr in feats.items():
        merged[name] = (("eta_rho", "xi_rho"), arr)
    return merged
