"""
Resolve and open WCOFS cycles from NOAA's public PDS bucket (``noaa-nos-ofs-pds``).

Listing-based key resolution supports legacy and post-SCN-24-77 naming and folder
layouts. Processed Zarr access remains in ``fishai.physics.store``.
"""

from __future__ import annotations

import datetime as dt
import io
import re
from collections.abc import Callable, Iterable, Sequence
from typing import Literal

import xarray as xr

from fishai.physics.store import CycleNotAvailable

WCOFS_PDS_BUCKET = "noaa-nos-ofs-pds"
WCOFS_NETCDF_ROOT = "wcofs/netcdf"
WCOFS_S3_HOST = f"{WCOFS_PDS_BUCKET}.s3.amazonaws.com"

NEW_STYLE_PREFER_START = dt.date(2024, 9, 1)
NEW_STYLE_PREFER_END = dt.date(2024, 9, 9)
PARALLEL_MODE_UNAVAILABLE_START = dt.date(2024, 7, 1)
PARALLEL_MODE_UNAVAILABLE_END = dt.date(2024, 8, 31)

_OLD_FIELDS_RE = re.compile(
    r"^nos\.wcofs\.fields\.(n\d{3}|f\d{3})\.(\d{8})\.t03z\.nc$"
)
_NEW_FIELDS_RE = re.compile(r"^wcofs\.t03z\.(\d{8})\.fields\.(n\d{3}|f\d{3})\.nc$")
_AVG_NOWCAST_RE = re.compile(r"^wcofs\.t03z\.(\d{8})\.avg\.nowcast\.nc$")

ListKeysFn = Callable[[str], Sequence[str]]


def _s3_url(key: str) -> str:
    return f"https://{WCOFS_S3_HOST}/{key.lstrip('/')}"


def layout_prefixes(day: dt.date) -> list[str]:
    """Return S3 key prefixes to search for ``day`` (most specific first)."""
    prefixes: list[str] = []
    if day >= dt.date(2025, 1, 3):
        prefixes.append(f"{WCOFS_NETCDF_ROOT}/{day:%Y/%m/%d}/")
    if day >= dt.date(2024, 11, 1):
        prefixes.append(f"{WCOFS_NETCDF_ROOT}/{day:%Y/%m}/")
    if dt.date(2024, 7, 1) <= day <= dt.date(2024, 12, 31):
        prefixes.append(f"{WCOFS_NETCDF_ROOT}/{day:%Y%m}/")
    return prefixes


def fields_basename_candidates(day: dt.date, lead: str) -> tuple[str, str]:
    """Return (new_style, old_style) basenames for one fields lead."""
    ymd = day.strftime("%Y%m%d")
    new_name = f"wcofs.t03z.{ymd}.fields.{lead}.nc"
    old_name = f"nos.wcofs.fields.{lead}.{ymd}.t03z.nc"
    return new_name, old_name


def avg_nowcast_basename(day: dt.date) -> str:
    return f"wcofs.t03z.{day:%Y%m%d}.avg.nowcast.nc"


def avg_nowcast_basename_candidates(day: dt.date) -> tuple[str, str]:
    """Return (new_style, legacy) basenames for ``avg.nowcast``."""
    ymd = day.strftime("%Y%m%d")
    return avg_nowcast_basename(day), f"nos.wcofs.avg.nowcast.{ymd}.t03z.nc"


def _basename_style(name: str) -> Literal["new", "old", "avg", "other"]:
    if _NEW_FIELDS_RE.match(name) or _AVG_NOWCAST_RE.match(name):
        return "new" if _NEW_FIELDS_RE.match(name) else "avg"
    if _OLD_FIELDS_RE.match(name):
        return "old"
    return "other"


def resolve_fields_key(
    day: dt.date,
    lead: str,
    list_keys: ListKeysFn,
) -> str:
    """
    Resolve exactly one S3 object key for WCOFS fields ``lead`` on ``day``.

    Raises ``CycleNotAvailable`` when no unique candidate exists.
    """
    new_base, old_base = fields_basename_candidates(day, lead)
    matches: list[tuple[str, Literal["new", "old"]]] = []
    for prefix in layout_prefixes(day):
        for key in list_keys(prefix):
            base = key.rsplit("/", 1)[-1]
            if base == new_base:
                matches.append((key, "new"))
            elif base == old_base:
                matches.append((key, "old"))
    if not matches:
        raise CycleNotAvailable(f"no WCOFS fields {lead} for {day.isoformat()} under {WCOFS_NETCDF_ROOT}")
    styles = {style for _, style in matches}
    if NEW_STYLE_PREFER_START <= day <= NEW_STYLE_PREFER_END and "new" in styles:
        chosen = [k for k, s in matches if s == "new"]
    else:
        chosen = [k for k, _ in matches]
    unique = sorted(set(chosen))
    if len(unique) != 1:
        raise CycleNotAvailable(
            f"ambiguous WCOFS fields {lead} for {day.isoformat()}: {unique[:5]}"
        )
    return unique[0]


def _choose_avg_nowcast_key(
    day: dt.date,
    matches: list[tuple[str, Literal["new", "old"]]],
) -> str:
    """Pick one key from matches inside a single prefix."""
    styles = {style for _, style in matches}
    # 2024-09-01..09 publish both names; prefer SCN 24-77 when it exists.
    # 2024-09-05 and 2024-09-06 have only the legacy name.
    if NEW_STYLE_PREFER_START <= day <= NEW_STYLE_PREFER_END and "new" in styles:
        chosen = [key for key, style in matches if style == "new"]
    else:
        chosen = [key for key, _style in matches]
    unique = sorted(set(chosen))
    if len(unique) != 1:
        raise CycleNotAvailable(f"no unique avg.nowcast for {day.isoformat()}")
    return unique[0]


def resolve_avg_nowcast_key(day: dt.date, list_keys: ListKeysFn) -> str:
    if day < dt.date(2024, 9, 1):
        raise CycleNotAvailable(f"avg.nowcast not published before 2024-09-01 ({day})")
    new_base, old_base = avg_nowcast_basename_candidates(day)
    # layout_prefixes is most-specific first. A basename copied into a later
    # folder (2024-11 YYYY/MM and YYYYMM) must not be treated as ambiguous.
    for prefix in layout_prefixes(day):
        matches: list[tuple[str, Literal["new", "old"]]] = []
        for key in list_keys(prefix):
            base = key.rsplit("/", 1)[-1]
            if base == new_base:
                matches.append((key, "new"))
            elif base == old_base:
                matches.append((key, "old"))
        if not matches:
            continue
        return _choose_avg_nowcast_key(day, matches)
    raise CycleNotAvailable(f"no unique avg.nowcast for {day.isoformat()}")


def _reject_parallel_mode_test_run(ds: xr.Dataset, day: dt.date) -> None:
    if not (PARALLEL_MODE_UNAVAILABLE_START <= day <= PARALLEL_MODE_UNAVAILABLE_END):
        return
    for attr in ds.attrs.values():
        if isinstance(attr, str) and "parallel mode" in attr.lower():
            raise CycleNotAvailable(f"WCOFS parallel-mode test run for {day.isoformat()}")


def open_wcofs_cycle(
    cycle_date: dt.date,
    *,
    product: Literal["fields", "avg_nowcast"] = "fields",
    lead: str = "n003",
    list_keys: ListKeysFn | None = None,
    get_bytes: Callable[..., bytes] | None = None,
    head_ok: Callable[[str], bool] | None = None,
) -> xr.Dataset:
    """
    Open one 03z WCOFS NetCDF cycle from the public PDS bucket (read-only).

    Parameters
    ----------
    cycle_date:
        UTC calendar date of the 03z cycle.
    product:
        ``fields`` for a single nowcast/forecast lead file, or ``avg_nowcast`` for
        the daily mean nowcast product (available from 2024-09-01).
    lead:
        ROMS lead token (e.g. ``n003``) when ``product='fields'``.
    list_keys:
        Callable ``prefix -> object keys`` (mocked in CI). When omitted, uses S3
        ListObjectsV2 via ``head_ok``/HTTP (not used in unit tests).
    get_bytes:
        Download callable; defaults to ``fishai.ingestion.physics.http_util.get_bytes``.
    """
    if list_keys is None:
        from fishai.ingestion.physics.wcofs_pds_s3_list import list_keys_under_prefix

        list_keys = list_keys_under_prefix
    if get_bytes is None:
        from fishai.ingestion.physics.http_util import get_bytes as _get_bytes

        get_bytes = _get_bytes

    if product == "avg_nowcast":
        key = resolve_avg_nowcast_key(cycle_date, list_keys)
    else:
        key = resolve_fields_key(cycle_date, lead, list_keys)

    url = _s3_url(key)
    if head_ok is not None and not head_ok(url):
        raise CycleNotAvailable(f"WCOFS object not reachable: {key}")

    data = get_bytes(url, extra_cache_key=key)
    engine = "h5netcdf" if data[:4] == b"\x89HDF" else "scipy"
    ds = xr.open_dataset(io.BytesIO(data), engine=engine, decode_times=False)
    _reject_parallel_mode_test_run(ds, cycle_date)
    ds.attrs.setdefault("wcofs_s3_key", key)
    ds.attrs.setdefault("cycle", f"{cycle_date.strftime('%Y%m%d')}T03Z")
    return ds


def cycle_available(
    day: dt.date,
    *,
    lead: str = "n024",
    list_keys: ListKeysFn | None = None,
) -> bool:
    """Return True when ``resolve_fields_key`` would succeed for ``lead``."""
    try:
        if list_keys is None:
            from fishai.ingestion.physics.wcofs_pds_s3_list import list_keys_under_prefix

            list_keys = list_keys_under_prefix
        resolve_fields_key(day, lead, list_keys)
        return True
    except CycleNotAvailable:
        return False
