"""NOAA public GCS mirrors for SWFSC CPS life-history CSV exports (ERDDAP 504 fallback)."""

from __future__ import annotations

import csv
import io
import urllib.request
from pathlib import Path
from typing import Any, Iterator, Mapping

from fishai.ingestion.biology.cps_nearshore.fetch import BBox
from fishai.ingestion.sources import REPO_ROOT

GCS_BASE = "https://storage.googleapis.com/nmfs_odp_swfsc/Fisheries%20Resources%20Division"

TRAWL_HAUL_CATCH_URL = f"{GCS_BASE}/CPS_Trawl_LifeHistory_HaulCatch.csv"
TRAWL_SPECIMEN_URL = f"{GCS_BASE}/CPS_Trawl_LifeHistory_Specimen.csv"
NEARSHORE_SET_CATCH_URL = f"{GCS_BASE}/CPS_Trawl_LifeHistory_Nearshore_SetCatch.csv"
NEARSHORE_SPECIMEN_URL = f"{GCS_BASE}/CPS_Trawl_LifeHistory_Nearshore_Specimen.csv"

DEFAULT_TIMEOUT_SEC = 300.0


def download_public_csv(url: str, dest: Path, *, timeout: float = DEFAULT_TIMEOUT_SEC) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "fishai-adult-cps-gcs/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        dest.write_bytes(resp.read())
    return dest


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "na", ""}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def in_pilot_bbox(row: Mapping[str, Any], bbox: BBox, *, lat_key: str, lon_key: str) -> bool:
    lat = _parse_float(row.get(lat_key))
    lon = _parse_float(row.get(lon_key))
    if lat is None or lon is None:
        return False
    return bbox.lat_min <= lat <= bbox.lat_max and bbox.lon_min <= lon <= bbox.lon_max


def normalize_trawl_haul_gcs_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Map InPort/GCS column names to ERDDAP-style keys used by ``parse_catch_row``."""
    return {
        "cruise": row.get("cruise"),
        "ship": row.get("ship"),
        "haul": row.get("haul"),
        "collection": row.get("collection"),
        "latitude": row.get("startLatitude") or row.get("latitude"),
        "longitude": row.get("startLongitude") or row.get("longitude"),
        "stop_latitude": row.get("stopLatitude") or row.get("stop_latitude"),
        "stop_longitude": row.get("stopLongitude") or row.get("stop_longitude"),
        "time": row.get("equilibriumTime") or row.get("time"),
        "haulback_time": row.get("haulBackTime") or row.get("haulback_time"),
        "surface_temp": row.get("surfaceTemp") or row.get("surface_temp"),
        "surface_temp_method": row.get("surfaceTempMethod") or row.get("surface_temp_method"),
        "ship_spd_through_water": row.get("shipSpeedThrougtheWater")
        or row.get("ship_spd_through_water"),
        "itis_tsn": row.get("itisTSN") or row.get("itis_tsn"),
        "scientific_name": row.get("scientificName") or row.get("scientific_name"),
        "subsample_count": row.get("subSampleCount") or row.get("subsample_count"),
        "subsample_weight": row.get("subSampleWeightkg") or row.get("subsample_weight"),
        "remaining_weight": row.get("remainingWeightkg") or row.get("remaining_weight"),
        "presence_only": row.get("presenceOnly") or row.get("presence_only"),
    }


def normalize_nearshore_set_gcs_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "cruise": row.get("cruise"),
        "ship": row.get("ship"),
        "date": row.get("date"),
        "time_PDT": row.get("time_PDT"),
        "time": row.get("datetime_UTC") or row.get("time"),
        "set": row.get("set"),
        "latitude": row.get("Latitude") or row.get("latitude"),
        "longitude": row.get("Longitude") or row.get("longitude"),
        "state": row.get("state"),
        "gearType": row.get("gearType"),
        "itis_tsn": row.get("itisTSN") or row.get("itis_tsn"),
        "scientific_name": row.get("scientificName") or row.get("scientific_name"),
        "totalNumber": row.get("totalNumber"),
        "totalWeightkg": row.get("totalWeightkg"),
    }


def normalize_trawl_specimen_gcs_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "cruise": row.get("cruise"),
        "ship": row.get("ship"),
        "haul": row.get("haul"),
        "latitude": row.get("Latitude") or row.get("latitude"),
        "longitude": row.get("Longitude") or row.get("longitude"),
        "time": row.get("Time") or row.get("time"),
        "itis_tsn": row.get("itisTSN") or row.get("itis_tsn"),
        "scientific_name": row.get("scientificName") or row.get("scientific_name"),
        "standard_length": row.get("standardLength_mm") or row.get("standard_length"),
        "fork_length": row.get("forkLength_mm") or row.get("fork_length"),
        "total_length": row.get("totalLength_mm") or row.get("total_length"),
    }


def normalize_nearshore_specimen_gcs_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "cruise": row.get("cruise"),
        "ship": row.get("ship"),
        "set": row.get("set"),
        "latitude": row.get("Latitude") or row.get("latitude"),
        "longitude": row.get("Longitude") or row.get("longitude"),
        "time": row.get("datetime_UTC") or row.get("time"),
        "itis_tsn": row.get("itisTSN") or row.get("itis_tsn"),
        "scientific_name": row.get("scientificName") or row.get("scientific_name"),
        "standard_length": row.get("standardLength_mm") or row.get("standard_length"),
        "fork_length": row.get("forkLength_mm") or row.get("fork_length"),
    }


def iter_gcs_csv_rows(path: Path) -> Iterator[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        yield dict(row)


def gcs_raw_dir() -> Path:
    return REPO_ROOT / "data" / "raw" / "swfsc_cps_gcs_mirror"
