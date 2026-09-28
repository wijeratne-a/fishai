"""IOOS Glider DAC ERDDAP profiles."""

from __future__ import annotations

import io
from datetime import datetime, timezone
from urllib.parse import quote

import pandas as pd

from fishai.ingestion.sensors.internal.config import load_sensors_config
from fishai.ingestion.sensors.internal.http import get_http_client

GLIDER_PROFILE_VARS = [
    "time",
    "latitude",
    "longitude",
    "depth",
    "temperature",
    "salinity",
    "profile_id",
]


def _iso_z(t: datetime) -> str:
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    else:
        t = t.astimezone(timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _glider_base() -> str:
    return load_sensors_config()["erddap"]["glider_dac"].rstrip("/")


def list_active(
    bbox: tuple[float, float, float, float],
    since: datetime,
    *,
    client=None,
) -> list[str]:
    """Dataset IDs intersecting bbox with data since ``since``."""
    la0, la1, lo0, lo1 = bbox
    def _c(param: str, op: str, val: str | float) -> str:
        return quote(f"{param}{op}{val}", safe="")

    url = (
        f"{_glider_base()}/tabledap/allDatasets.csv?datasetID,minTime,maxTime"
        f"&{_c('minLatitude', '<=', la1)}"
        f"&{_c('maxLatitude', '>=', la0)}"
        f"&{_c('minLongitude', '<=', lo1)}"
        f"&{_c('maxLongitude', '>=', lo0)}"
        f"&{_c('maxTime', '>=', _iso_z(since))}"
    )
    http = client or get_http_client()
    resp = http.get(url, accept_404=True)
    if resp.status_code == 404:
        return []
    df = pd.read_csv(io.StringIO(resp.text), skiprows=[1], low_memory=False)
    if df.empty or "datasetID" not in df.columns:
        return []
    return sorted(df["datasetID"].astype(str).unique().tolist())


def build_glider_profile_url(
    dataset_id: str,
    t0: datetime,
    t1: datetime,
) -> str:
    q = ",".join(GLIDER_PROFILE_VARS)
    def _c(param: str, op: str, val: str) -> str:
        return quote(f"{param}{op}{val}", safe="")

    return (
        f"{_glider_base()}/tabledap/{dataset_id}.csv?{q}"
        f"&{_c('time', '>=', _iso_z(t0))}"
        f"&{_c('time', '<=', _iso_z(t1))}"
    )


def fetch_profiles(
    dataset_id: str,
    t0: datetime,
    t1: datetime,
    *,
    client=None,
) -> pd.DataFrame:
    """T/S by depth per profile for one glider dataset."""
    http = client or get_http_client()
    url = build_glider_profile_url(dataset_id, t0, t1)
    resp = http.get(url, accept_404=True)
    if resp.status_code == 404:
        return pd.DataFrame(columns=GLIDER_PROFILE_VARS)
    df = pd.read_csv(io.StringIO(resp.text), skiprows=[1], low_memory=False)
    if not df.empty:
        df["time"] = pd.to_datetime(df["time"], utc=True)
        df["dataset_id"] = dataset_id
    df.attrs["source_url"] = url
    return df
