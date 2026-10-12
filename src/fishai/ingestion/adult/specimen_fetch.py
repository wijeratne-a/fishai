"""Public ERDDAP fetch for CPS trawl and nearshore specimen tables (no species URL filters)."""

from __future__ import annotations

import csv
import io
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import quote

from fishai.ingestion.biology.cps_trawl.fetch import BBox, iter_yearly_windows
from fishai.ingestion.biology.cufes.erddap_rows import is_erddap_units_row
from fishai.ingestion.sources import REPO_ROOT, require_approved

TRAWL_SPECIMEN_BASE = "https://oceanview.pfeg.noaa.gov/erddap/tabledap/FRDCPSTrawlLHSpecimen"
NEARSHORE_SPECIMEN_BASE = "https://oceanview.pfeg.noaa.gov/erddap/tabledap/FRDCPSNearshoreSpecimen"

TRAWL_SPECIMEN_FIELDS: Sequence[str] = (
    "cruise",
    "ship",
    "haul",
    "latitude",
    "longitude",
    "time",
    "itis_tsn",
    "scientific_name",
    "standard_length",
    "fork_length",
    "total_length",
)

NEARSHORE_SPECIMEN_FIELDS: Sequence[str] = (
    "cruise",
    "ship",
    "set",
    "latitude",
    "longitude",
    "time",
    "itis_tsn",
    "scientific_name",
    "standard_length",
    "fork_length",
)

DEFAULT_TIMEOUT_SEC = 120.0
DEFAULT_MAX_RETRIES = 5
DEFAULT_BACKOFF_SEC = 2.0


def _erddap_time(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%d")


def build_specimen_csv_url(
    base: str,
    fields: Sequence[str],
    t0: datetime,
    t1: datetime,
    bbox: BBox | None,
) -> str:
    field_list = ",".join(fields)

    def c(name: str, op: str, value: str) -> str:
        enc_val = quote(str(value), safe="")
        if op == ">=":
            return f"{name}%3E={enc_val}"
        if op == "<=":
            return f"{name}%3C={enc_val}"
        if op == "<":
            return f"{name}%3C{enc_val}"
        raise ValueError(f"unsupported ERDDAP constraint operator: {op}")

    constraints = [
        c("time", ">=", _erddap_time(t0)),
        c("time", "<", _erddap_time(t1)),
    ]
    if bbox is not None:
        constraints.extend(
            [
                c("latitude", ">=", f"{bbox.lat_min}"),
                c("latitude", "<=", f"{bbox.lat_max}"),
                c("longitude", ">=", f"{bbox.lon_min}"),
                c("longitude", "<=", f"{bbox.lon_max}"),
            ]
        )
    query = f"{field_list}&" + "&".join(constraints)
    return f"{base}.csv?{query}"


def _http_get(url: str, *, timeout: float, max_retries: int, backoff: float) -> bytes:
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "fishai-adult-cps-specimens/0.1"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise
            last_err = exc
            if attempt + 1 < max_retries:
                time.sleep(backoff * (2**attempt))
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
            if attempt + 1 < max_retries:
                time.sleep(backoff * (2**attempt))
    raise RuntimeError(f"ERDDAP fetch failed after {max_retries} attempts: {last_err}") from last_err


def read_specimen_csv(path: Path) -> tuple[list[dict[str, Any]], int]:
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    rows: list[dict[str, Any]] = []
    skipped = 0
    saw_data_row = False
    for data_row_index, row in enumerate(reader):
        saw_data_row = True
        if is_erddap_units_row(row, data_row_index=data_row_index, path=path):
            skipped += 1
            continue
        rows.append(dict(row))
    if not saw_data_row:
        raise ValueError(f"expected ERDDAP units row as first data line in {path}, file has no data rows")
    if skipped == 0:
        raise ValueError(f"expected ERDDAP units row as first data line in {path}, no units row was skipped")
    return rows, skipped


def _fetch_windows(
    *,
    base: str,
    fields: Sequence[str],
    windows: list[tuple[datetime, datetime]],
    bbox: BBox | None,
    dest_dir: Path,
    filename_prefix: str,
) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for win_start, win_end in windows:
        url = build_specimen_csv_url(base, fields, win_start, win_end, bbox)
        label = win_start.strftime("%Y%m%d")
        dest = dest_dir / f"{filename_prefix}_{label}.csv"
        try:
            body = _http_get(url, timeout=DEFAULT_TIMEOUT_SEC, max_retries=DEFAULT_MAX_RETRIES, backoff=DEFAULT_BACKOFF_SEC)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            raise
        dest.write_bytes(body)
        written.append(dest)
    return written


def fetch_trawl_specimens(
    t0: date,
    t1: date,
    bbox: BBox | None,
    *,
    dest_dir: Path | None = None,
) -> list[Path]:
    require_approved("swfsc_cps_trawl_haul_catch")
    out = dest_dir or (REPO_ROOT / "data" / "raw" / "swfsc_cps_trawl_haul_catch" / "specimens")
    windows = iter_yearly_windows(t0, t1)
    return _fetch_windows(
        base=TRAWL_SPECIMEN_BASE,
        fields=TRAWL_SPECIMEN_FIELDS,
        windows=windows,
        bbox=bbox,
        dest_dir=out,
        filename_prefix="FRDCPSTrawlLHSpecimen",
    )


def iter_halfyear_windows(t0: date, t1: date) -> list[tuple[datetime, datetime]]:
    """Six-month batches clipped to [t0, t1] (nearshore mirror fallback)."""
    if t1 < t0:
        return []
    range_start = datetime.combine(t0, datetime.min.time(), tzinfo=timezone.utc)
    range_end = datetime.combine(t1 + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    windows: list[tuple[datetime, datetime]] = []
    for year in range(t0.year, t1.year + 1):
        for month_start, month_end in ((1, 7), (7, 13)):
            win_start = datetime(year, month_start, 1, tzinfo=timezone.utc)
            win_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc) if month_end == 13 else datetime(
                year, month_end, 1, tzinfo=timezone.utc
            )
            clip_start = max(win_start, range_start)
            clip_end = min(win_end, range_end)
            if clip_start < clip_end:
                windows.append((clip_start, clip_end))
    return windows


def fetch_nearshore_specimens(
    t0: date,
    t1: date,
    bbox: BBox | None,
    *,
    dest_dir: Path | None = None,
    half_year: bool = False,
) -> list[Path]:
    require_approved("swfsc_cps_nearshore_set_catch")
    out = dest_dir or (REPO_ROOT / "data" / "raw" / "swfsc_cps_nearshore_set_catch" / "specimens")
    windows = iter_halfyear_windows(t0, t1) if half_year else [
        (a, b) for a, b in iter_yearly_windows(t0, t1)
    ]
    return _fetch_windows(
        base=NEARSHORE_SPECIMEN_BASE,
        fields=NEARSHORE_SPECIMEN_FIELDS,
        windows=windows,
        bbox=bbox,
        dest_dir=out,
        filename_prefix="FRDCPSNearshoreSpecimen",
    )
