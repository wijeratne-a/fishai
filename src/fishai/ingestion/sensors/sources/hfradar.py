"""SCCOOS HF radar (ucsdHfrW6) via CoastWatch ERDDAP griddap."""

from __future__ import annotations

import io
from datetime import datetime, timedelta, timezone

import xarray as xr

from fishai.ingestion.sensors.internal.config import load_sensors_config, pilot_bbox
from fishai.ingestion.sensors.internal.http import get_http_client

HFR_DATASET = "ucsdHfrW6"
HFR_VARS = (
    "water_u",
    "water_v",
    "DOPx",
    "DOPy",
    "hdop",
    "number_of_sites",
    "number_of_radials",
)


def closed_hour_window(
    now: datetime | None = None,
    hours: int = 24,
) -> tuple[datetime, datetime]:
    """Return UTC [t0, t1] for the last ``hours`` complete hours (exclude current partial hour)."""
    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)
    hour_top = now.replace(minute=0, second=0, microsecond=0)
    t1 = hour_top - timedelta(hours=1)
    t0 = t1 - timedelta(hours=hours - 1)
    return t0, t1


def _iso_z(t: datetime) -> str:
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    else:
        t = t.astimezone(timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_hfr_griddap_url(
    bbox: tuple[float, float, float, float],
    *,
    t0: datetime | None = None,
    t1: datetime | None = None,
    use_relative_last: bool = False,
    relative_start: str = "last-5",
    fmt: str = "nc",
) -> str:
    """Build griddap URL. ERDDAP relative indices must NOT be parenthesized."""
    cfg = load_sensors_config()
    base = cfg["erddap"]["coastwatch"].rstrip("/")
    la0, la1, lo0, lo1 = bbox
    sp = f"[({la0}):1:({la1})][({lo0}):1:({lo1})]"
    if use_relative_last:
        ts = f"[{relative_start}:1:last]"
    elif t0 is not None and t1 is not None:
        ts = f"[({_iso_z(t0)}):1:({_iso_z(t1)})]"
    else:
        ts = "[last-24:1:last-1]"
    q = ",".join(f"{v}{ts}{sp}" for v in HFR_VARS)
    return f"{base}/griddap/{HFR_DATASET}.{fmt}?{q}"


def fetch_hfr(
    t0: datetime,
    t1: datetime,
    bbox: tuple[float, float, float, float],
    *,
    client=None,
) -> xr.Dataset:
    """Fetch HF radar gridded vectors for the closed interval [t0, t1] (hourly)."""
    http = client or get_http_client()
    url = build_hfr_griddap_url(bbox, t0=t0, t1=t1)
    resp = http.get(url, accept_404=False)
    if resp.status_code != 200:
        raise RuntimeError(f"HF radar fetch failed ({resp.status_code})")
    ds = xr.open_dataset(io.BytesIO(resp.content))
    ds = ds.load()
    ds.attrs["source_url"] = url
    ds.attrs["fetcher"] = "fishai.ingestion.sensors.sources.hfradar"
    return ds


def fetch_hfr_sync_window(
    bbox: tuple[float, float, float, float] | None = None,
    *,
    hours: int = 24,
    client=None,
) -> xr.Dataset:
    """Sync helper: last ``hours`` closed hours, skipping the current partial hour."""
    bbox = bbox or pilot_bbox()
    t0, t1 = closed_hour_window(hours=hours)
    return fetch_hfr(t0, t1, bbox, client=client)
