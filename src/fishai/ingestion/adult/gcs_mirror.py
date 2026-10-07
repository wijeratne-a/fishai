"""Public NOAA SWFSC CPS CSV mirrors on Google Cloud Storage (InPort download URLs).

Used when ERDDAP tabledap requests time out (504). Source files use column names that differ
from ERDDAP tabledap CSV; normalizers map rows to the ERDDAP field names expected by ingest.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path
from typing import Any, Mapping

from fishai.ingestion.sources import REPO_ROOT

GCS_BASE = "https://storage.googleapis.com/nmfs_odp_swfsc/Fisheries%20Resources%20Division"

GCS_TRAWL_HAUL_CATCH = f"{GCS_BASE}/CPS_Trawl_LifeHistory_HaulCatch.csv"
GCS_TRAWL_SPECIMEN = f"{GCS_BASE}/CPS_Trawl_LifeHistory_Specimen.csv"
GCS_NEARSHORE_SET_CATCH = f"{GCS_BASE}/CPS_Trawl_LifeHistory_Nearshore_SetCatch.csv"
GCS_NEARSHORE_SPECIMEN = f"{GCS_BASE}/CPS_Trawl_LifeHistory_Nearshore_Specimen.csv"

DEFAULT_MIRROR_DIR = REPO_ROOT / "data" / "raw" / "swfsc_cps_gcs_mirror"


def download_gcs_csv(url: str, dest: Path, *, timeout: float = 600.0) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "fishai-adult-cps-gcs/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        dest.write_bytes(resp.read())
    return dest


def normalize_trawl_haul_catch_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "cruise": row.get("cruise") or row.get("Cruise"),
        "ship": row.get("ship") or row.get("Ship"),
        "haul": row.get("haul") or row.get("Haul"),
        "collection": row.get("collection") or row.get("Collection"),
        "latitude": row.get("latitude") or row.get("startLatitude") or row.get("Latitude"),
        "longitude": row.get("longitude") or row.get("startLongitude") or row.get("Longitude"),
        "stop_latitude": row.get("stop_latitude") or row.get("stopLatitude"),
        "stop_longitude": row.get("stop_longitude") or row.get("stopLongitude"),
        "time": row.get("time") or row.get("equilibriumTime") or row.get("Time"),
        "haulback_time": row.get("haulback_time") or row.get("haulBackTime"),
        "surface_temp": row.get("surface_temp") or row.get("surfaceTemp"),
        "surface_temp_method": row.get("surface_temp_method") or row.get("surfaceTempMethod"),
        "ship_spd_through_water": row.get("ship_spd_through_water")
        or row.get("shipSpeedThrougtheWater"),
        "itis_tsn": row.get("itis_tsn") or row.get("itisTSN"),
        "scientific_name": row.get("scientific_name") or row.get("scientificName"),
        "subsample_count": row.get("subsample_count") or row.get("subSampleCount"),
        "subsample_weight": row.get("subsample_weight") or row.get("subSampleWeightkg"),
        "remaining_weight": row.get("remaining_weight") or row.get("remainingWeightkg"),
        "presence_only": row.get("presence_only") or row.get("presenceOnly"),
    }


def normalize_trawl_specimen_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "cruise": row.get("cruise"),
        "ship": row.get("ship"),
        "haul": row.get("haul"),
        "latitude": row.get("latitude") or row.get("Latitude"),
        "longitude": row.get("longitude") or row.get("Longitude"),
        "time": row.get("time") or row.get("Time"),
        "itis_tsn": row.get("itis_tsn") or row.get("itisTSN"),
        "scientific_name": row.get("scientific_name") or row.get("scientificName"),
        "standard_length": row.get("standard_length") or row.get("standardLength_mm"),
        "fork_length": row.get("fork_length") or row.get("forkLength_mm"),
        "total_length": row.get("total_length") or row.get("totalLength_mm"),
    }


def normalize_nearshore_set_catch_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "cruise": row.get("cruise"),
        "ship": row.get("ship"),
        "date": row.get("date"),
        "time_PDT": row.get("time_PDT"),
        "time": row.get("time") or row.get("datetime_UTC"),
        "set": row.get("set") or row.get("Set"),
        "latitude": row.get("latitude") or row.get("Latitude"),
        "longitude": row.get("longitude") or row.get("Longitude"),
        "state": row.get("state"),
        "gearType": row.get("gearType"),
        "itis_tsn": row.get("itis_tsn") or row.get("itisTSN"),
        "scientific_name": row.get("scientific_name") or row.get("scientificName"),
        "totalNumber": row.get("totalNumber"),
        "totalWeightkg": row.get("totalWeightkg"),
    }


def normalize_nearshore_specimen_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "cruise": row.get("cruise"),
        "ship": row.get("ship"),
        "set": row.get("set"),
        "latitude": row.get("latitude") or row.get("Latitude"),
        "longitude": row.get("longitude") or row.get("Longitude"),
        "time": row.get("time") or row.get("datetime_UTC"),
        "itis_tsn": row.get("itis_tsn") or row.get("itisTSN"),
        "scientific_name": row.get("scientific_name") or row.get("scientificName"),
        "standard_length": row.get("standard_length"),
        "fork_length": row.get("fork_length"),
    }
