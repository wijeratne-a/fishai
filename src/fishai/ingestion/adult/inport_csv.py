"""Normalize NOAA InPort / GCS CPS CSV column names to ERDDAP-style fields."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any, Mapping


def _strip_keys(row: Mapping[str, Any]) -> dict[str, Any]:
    return {str(k).strip(): v for k, v in row.items()}


def normalize_trawl_haul_catch_row(row: Mapping[str, Any]) -> dict[str, Any]:
    r = _strip_keys(row)
    return {
        "cruise": r.get("cruise"),
        "ship": r.get("ship"),
        "haul": r.get("haul"),
        "collection": r.get("collection"),
        "latitude": r.get("startLatitude", r.get("latitude")),
        "longitude": r.get("startLongitude", r.get("longitude")),
        "stop_latitude": r.get("stopLatitude", r.get("stop_latitude")),
        "stop_longitude": r.get("stopLongitude", r.get("stop_longitude")),
        "time": r.get("equilibriumTime", r.get("time")),
        "haulback_time": r.get("haulBackTime", r.get("haulback_time")),
        "surface_temp": r.get("surfaceTemp", r.get("surface_temp")),
        "surface_temp_method": r.get("surfaceTempMethod", r.get("surface_temp_method")),
        "ship_spd_through_water": r.get("shipSpeedThrougtheWater", r.get("ship_spd_through_water")),
        "itis_tsn": r.get("itisTSN", r.get("itis_tsn")),
        "scientific_name": r.get("scientificName", r.get("scientific_name")),
        "subsample_count": r.get("subSampleCount", r.get("subsample_count")),
        "subsample_weight": r.get("subSampleWeightkg", r.get("subsample_weight")),
        "remaining_weight": r.get("remainingWeightkg", r.get("remaining_weight")),
        "presence_only": r.get("presenceOnly", r.get("presence_only")),
    }


def normalize_nearshore_set_catch_row(row: Mapping[str, Any]) -> dict[str, Any]:
    r = _strip_keys(row)
    return {
        "cruise": r.get("cruise"),
        "ship": r.get("ship"),
        "date": r.get("date"),
        "time_PDT": r.get("time_PDT"),
        "time": r.get("datetime_UTC", r.get("time")),
        "set": r.get("set"),
        "latitude": r.get("Latitude", r.get("latitude")),
        "longitude": r.get("Longitude", r.get("longitude")),
        "state": r.get("state"),
        "gearType": r.get("gearType"),
        "itis_tsn": r.get("itisTSN", r.get("itis_tsn")),
        "scientific_name": r.get("scientificName", r.get("scientific_name")),
        "totalNumber": r.get("totalNumber"),
        "totalWeightkg": r.get("totalWeightkg"),
    }


def normalize_trawl_specimen_row(row: Mapping[str, Any]) -> dict[str, Any]:
    r = _strip_keys(row)
    return {
        "cruise": r.get("cruise"),
        "ship": r.get("ship"),
        "haul": r.get("haul"),
        "latitude": r.get("Latitude", r.get("latitude")),
        "longitude": r.get("Longitude", r.get("longitude")),
        "time": r.get("Time", r.get("time")),
        "itis_tsn": r.get("itisTSN", r.get("itis_tsn")),
        "scientific_name": r.get("scientificName", r.get("scientific_name")),
        "standard_length": r.get("standardLength_mm", r.get("standard_length")),
        "fork_length": r.get("forkLength_mm", r.get("fork_length")),
        "total_length": r.get("totalLength_mm", r.get("total_length")),
    }


def normalize_nearshore_specimen_row(row: Mapping[str, Any]) -> dict[str, Any]:
    r = _strip_keys(row)
    return {
        "cruise": r.get("cruise"),
        "ship": r.get("ship"),
        "set": r.get("set"),
        "latitude": r.get("Latitude", r.get("latitude")),
        "longitude": r.get("Longitude", r.get("longitude")),
        "time": r.get("Time", r.get("time")),
        "itis_tsn": r.get("itisTSN", r.get("itis_tsn")),
        "scientific_name": r.get("scientificName", r.get("scientific_name")),
        "standard_length": r.get("standardLength_mm", r.get("standard_length")),
        "fork_length": r.get("forkLength_mm", r.get("fork_length")),
    }


def read_inport_csv(path: Path, normalizer) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    return [normalizer(row) for row in reader]
