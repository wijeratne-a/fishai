"""NDBC standard meteorological/ocean (cwwcNDBCMet) via CoastWatch ERDDAP."""

from __future__ import annotations

import io
from datetime import datetime, timezone
from urllib.parse import quote

import pandas as pd

from fishai.ingestion.sensors.internal.config import load_sensors_config, pilot_bbox
from fishai.ingestion.sensors.internal.http import get_http_client

NDBC_DATASET = "cwwcNDBCMet"
NDBC_VARS = [
    "station",
    "time",
    "latitude",
    "longitude",
    "WD",
    "WSPD",
    "GST",
    "WVHT",
    "DPD",
    "APD",
    "MWD",
    "BAR",
    "ATMP",
    "WTMP",
    "DEWP",
]


def _iso_z(t: datetime) -> str:
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    else:
        t = t.astimezone(timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _erddap_base() -> str:
    return load_sensors_config()["erddap"]["coastwatch"].rstrip("/")


def list_stations(
    bbox: tuple[float, float, float, float],
    *,
    client=None,
) -> list[str]:
    """Return station IDs with WTMP in the bbox (recent snapshot)."""
    la0, la1, lo0, lo1 = bbox
    q = ",".join(["station", "WTMP"])
    # Percent-encode comparison operators for ERDDAP constraints.
    url = (
        f"{_erddap_base()}/tabledap/{NDBC_DATASET}.csv?{q}"
        f"&time=last"
        f"&latitude>={la0}&latitude<={la1}"
        f"&longitude>={lo0}&longitude<={lo1}"
    )
    http = client or get_http_client()
    resp = http.get(url, accept_404=True)
    if resp.status_code == 404:
        return []
    df = pd.read_csv(io.StringIO(resp.text), skiprows=[1], low_memory=False)
    if df.empty or "WTMP" not in df.columns:
        return []
    df = df.dropna(subset=["WTMP"])
    if "station" not in df.columns:
        return []
    return sorted(df["station"].astype(str).unique().tolist())


def build_ndbc_url(
    t0: datetime,
    t1: datetime,
    bbox: tuple[float, float, float, float],
    stations: list[str] | None = None,
) -> str:
    la0, la1, lo0, lo1 = bbox
    q = ",".join(NDBC_VARS)
    def _c(param: str, op: str, val: str | float) -> str:
        return quote(f"{param}{op}{val}", safe="")

    parts = [
        f"{_erddap_base()}/tabledap/{NDBC_DATASET}.csv?{q}",
        f"&{_c('time', '>=', _iso_z(t0))}",
        f"&{_c('time', '<=', _iso_z(t1))}",
        f"&{_c('latitude', '>=', la0)}",
        f"&{_c('latitude', '<=', la1)}",
        f"&{_c('longitude', '>=', lo0)}",
        f"&{_c('longitude', '<=', lo1)}",
    ]
    if stations:
        station_filter = "|".join(stations)
        parts.append(f"&station=({station_filter})")
    return "".join(parts)


def fetch_ndbc(
    t0: datetime,
    t1: datetime,
    bbox: tuple[float, float, float, float],
    stations: list[str] | None = None,
    *,
    client=None,
) -> pd.DataFrame:
    """Fetch NDBC met/ocean rows; drop shore stations with no WTMP."""
    http = client or get_http_client()
    url = build_ndbc_url(t0, t1, bbox, stations)
    resp = http.get(url, accept_404=True)
    if resp.status_code == 404:
        return pd.DataFrame(columns=NDBC_VARS)
    df = pd.read_csv(io.StringIO(resp.text), skiprows=[1], low_memory=False)
    if df.empty:
        return df
    df["time"] = pd.to_datetime(df["time"], utc=True)
    if "WTMP" in df.columns:
        has_wtmp = df.groupby("station")["WTMP"].apply(lambda s: s.notna().any())
        keep = has_wtmp[has_wtmp].index.astype(str).tolist()
        df = df[df["station"].astype(str).isin(keep)]
    df.attrs["source_url"] = url
    return df
