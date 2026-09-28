"""ERDDAP fetch for CalCOFI CUFES (batch/scheduled only)."""

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

from fishai.ingestion.biology.cufes.constants import ERDDAP_FIELDS, ERDDAP_TABLEDAP_BASE, SOURCE_ID
from fishai.ingestion.biology.cufes.erddap_rows import is_erddap_units_row
from fishai.ingestion.sources import REPO_ROOT, require_approved

DEFAULT_TIMEOUT_SEC = 120.0
DEFAULT_MAX_RETRIES = 5
DEFAULT_BACKOFF_SEC = 2.0


class BBox:
    """Axis-aligned bounding box (degrees)."""

    __slots__ = ("lat_min", "lat_max", "lon_min", "lon_max")

    def __init__(self, lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> None:
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max


def raw_dir() -> Path:
    return REPO_ROOT / "data" / "raw" / "calcofi_cufes"


def build_erddap_csv_url(
    t0: datetime,
    t1: datetime,
    bbox: BBox,
    *,
    fields: Sequence[str] = ERDDAP_FIELDS,
) -> str:
    """Build a tabledap CSV URL with percent-encoded constraint operators."""
    field_list = ",".join(fields)
    # ERDDAP requires >= and < as %3E= and %3C (or %3C= for <=).
    def c(name: str, op: str, value: str) -> str:
        enc_val = quote(str(value), safe="")
        if op == ">=":
            return f"{name}%3E={enc_val}"
        if op == "<=":
            return f"{name}%3C={enc_val}"
        if op == "<":
            return f"{name}%3C{enc_val}"
        if op == ">":
            return f"{name}%3E{enc_val}"
        raise ValueError(f"unsupported ERDDAP constraint operator: {op}")

    constraints = [
        c("time", ">=", _erddap_time(t0)),
        c("time", "<", _erddap_time(t1)),
        c("latitude", ">=", f"{bbox.lat_min}"),
        c("latitude", "<=", f"{bbox.lat_max}"),
        c("longitude", ">=", f"{bbox.lon_min}"),
        c("longitude", "<=", f"{bbox.lon_max}"),
    ]
    query = f"{field_list}&" + "&".join(constraints)
    return f"{ERDDAP_TABLEDAP_BASE}.csv?{query}"


def _erddap_time(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    # ERDDAP tabledap constraints accept calendar dates for this dataset.
    return dt.strftime("%Y-%m-%d")


def iter_yearly_windows(
    t0: date,
    t1: date,
) -> list[tuple[datetime, datetime]]:
    """Inclusive calendar-year batches clipped to [t0, t1]."""
    if t1 < t0:
        return []
    range_start = datetime.combine(t0, datetime.min.time(), tzinfo=timezone.utc)
    range_end = datetime.combine(t1 + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    windows: list[tuple[datetime, datetime]] = []
    year = t0.year
    while year <= t1.year:
        win_start = datetime(year, 1, 1, tzinfo=timezone.utc)
        win_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        clip_start = max(win_start, range_start)
        clip_end = min(win_end, range_end)
        if clip_start < clip_end:
            windows.append((clip_start, clip_end))
        year += 1
    return windows


def _http_get(url: str, *, timeout: float, max_retries: int, backoff: float) -> bytes:
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "fishai-cufes-ingest/0.1"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last_err = exc
            if attempt + 1 < max_retries:
                time.sleep(backoff * (2**attempt))
    raise RuntimeError(f"ERDDAP fetch failed after {max_retries} attempts: {last_err}") from last_err


def fetch_cufes(
    t0: date,
    t1: date,
    bbox: BBox,
    *,
    dest_dir: Path | None = None,
    timeout: float = DEFAULT_TIMEOUT_SEC,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff: float = DEFAULT_BACKOFF_SEC,
    manifest_path: Path | None = None,
) -> list[Path]:
    """
    Download CUFES rows for the window and bbox into ``data/raw/calcofi_cufes/``.

    One HTTP request per calendar year (sequential). Requires ``calcofi_cufes`` approved
    in ``data/SOURCES.yaml``.
    """
    require_approved(SOURCE_ID, path=manifest_path)
    out_dir = dest_dir or raw_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for win_start, win_end in iter_yearly_windows(t0, t1):
        url = build_erddap_csv_url(win_start, win_end, bbox)
        year_label = win_start.year
        dest = out_dir / f"erdCalCOFIcufes_{year_label}.csv"
        body = _http_get(url, timeout=timeout, max_retries=max_retries, backoff=backoff)
        dest.write_bytes(body)
        written.append(dest)
    return written


def read_cufes_csv(path: Path) -> tuple[list[dict[str, Any]], int]:
    """Return (data rows, units_rows_skipped)."""
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    rows: list[dict[str, Any]] = []
    skipped = 0
    for data_row_index, row in enumerate(reader):
        if is_erddap_units_row(row, data_row_index=data_row_index):
            skipped += 1
            continue
        rows.append(dict(row))
    return rows, skipped
