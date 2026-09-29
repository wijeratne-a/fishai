"""Scripps Spray glider binned profiles (ERDDAP tabledap, pilot subset)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Sequence
from urllib.parse import urlencode

import pandas as pd
import requests

from fishai.ingestion.sources import REPO_ROOT

SPRAY_ERDDAP_BASE = "https://spraydata.ucsd.edu/erddap/tabledap"
SPRAY_DATASETS = ("binnedCUGN80", "binnedCUGN90")
SPRAY_VARIABLES = (
    "profile",
    "mission",
    "depth",
    "time",
    "latitude",
    "longitude",
    "temperature",
    "salinity",
    "doxy",
)
DEFAULT_CACHE_PATH = (
    REPO_ROOT / "artifacts" / "harmonization" / "spray_glider" / "pilot_subset.parquet"
)
FIXTURE_CSV_PATH = REPO_ROOT / "tests" / "fixtures" / "spray_glider_pilot.csv"
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "spray_glider_pilot.parquet"

PILOT_LAT_MIN = 32.0
PILOT_LAT_MAX = 35.0
PILOT_LON_MIN = -121.0
PILOT_LON_MAX = -117.0


def _erddap_subset_url(
    dataset: str,
    *,
    start: dt.datetime,
    end: dt.datetime,
) -> str:
    constraints = [
        ("time>=", start.strftime("%Y-%m-%dT%H:%M:%SZ")),
        ("time<=", end.strftime("%Y-%m-%dT%H:%M:%SZ")),
        (f"latitude>=", str(PILOT_LAT_MIN)),
        (f"latitude<=", str(PILOT_LAT_MAX)),
        (f"longitude>=", str(PILOT_LON_MIN)),
        (f"longitude<=", str(PILOT_LON_MAX)),
    ]
    query = ",".join(SPRAY_VARIABLES)
    base = f"{SPRAY_ERDDAP_BASE}/{dataset}.csv?{query}"
    suffix = "&".join(f"{k}{v}" for k, v in constraints)
    return f"{base}&{suffix}"


def fetch_spray_glider_subset(
    *,
    test_start: dt.date,
    test_end: dt.date,
    datasets: Sequence[str] = SPRAY_DATASETS,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    """Download pilot-box Spray profiles for the test window (network)."""
    start = dt.datetime.combine(test_start, dt.time.min, tzinfo=dt.timezone.utc)
    end = dt.datetime.combine(test_end, dt.time.max.replace(microsecond=0), tzinfo=dt.timezone.utc)
    sess = session or requests.Session()
    frames: list[pd.DataFrame] = []
    for ds in datasets:
        url = _erddap_subset_url(ds, start=start, end=end)
        resp = sess.get(url, timeout=120)
        resp.raise_for_status()
        frame = pd.read_csv(resp.text)
        frame["dataset"] = ds
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    return _normalize_spray_frame(out)


def _normalize_spray_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.rename(
        columns={
            "temperature": "temperature_c",
            "salinity": "salinity_psu",
        }
    )
    out["time"] = pd.to_datetime(out["time"], utc=True)
    out["depth"] = pd.to_numeric(out["depth"], errors="coerce")
    out["latitude"] = pd.to_numeric(out["latitude"], errors="coerce")
    out["longitude"] = pd.to_numeric(out["longitude"], errors="coerce")
    out["profile_id"] = out["profile"].astype(str) + "_" + out["dataset"].astype(str)
    return out


def write_spray_glider_cache(df: pd.DataFrame, path: Path | str | None = None) -> Path:
    target = Path(path) if path is not None else DEFAULT_CACHE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(target, index=False)
    return target


def load_spray_glider_profiles(path: Path | str | None = None) -> pd.DataFrame:
    """Load cached Spray profiles (Parquet). CI uses ``tests/fixtures/spray_glider_pilot.parquet``."""
    p = Path(path) if path is not None else DEFAULT_CACHE_PATH
    if not p.is_file() and FIXTURE_PATH.is_file():
        p = FIXTURE_PATH
    if not p.is_file() and FIXTURE_CSV_PATH.is_file():
        return _normalize_spray_frame(pd.read_csv(FIXTURE_CSV_PATH))
    if not p.is_file():
        raise FileNotFoundError(f"Spray glider profile cache not found: {p}")
    return _normalize_spray_frame(pd.read_parquet(p))
