"""Map NOAA GCS mirror CSV column names to ERDDAP-style fields for CPS ingestion."""

from __future__ import annotations

from typing import Any, Mapping

GCS_TRAWL_CATCH_MAP: dict[str, str] = {
    "startLatitude": "latitude",
    "startLongitude": "longitude",
    "stopLatitude": "stop_latitude",
    "stopLongitude": "stop_longitude",
    "equilibriumTime": "time",
    "haulBackTime": "haulback_time",
    "surfaceTemp": "surface_temp",
    "surfaceTempMethod": "surface_temp_method",
    "shipSpeedThrougtheWater": "ship_spd_through_water",
    "itisTSN": "itis_tsn",
    "scientificName": "scientific_name",
    "subSampleCount": "subsample_count",
    "subSampleWeightkg": "subsample_weight",
    "remainingWeightkg": "remaining_weight",
    "presenceOnly": "presence_only",
}

GCS_TRAWL_SPECIMEN_MAP: dict[str, str] = {
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Time": "time",
    "itisTSN": "itis_tsn",
    "scientificName": "scientific_name",
    "standardLength_mm": "standard_length",
    "forkLength_mm": "fork_length",
    "totalLength_mm": "total_length",
}

GCS_NEARSHORE_CATCH_MAP: dict[str, str] = {
    "Latitude": "latitude",
    "Longitude": "longitude",
    "datetime_UTC": "time",
    "itisTSN": "itis_tsn",
    "scientificName": "scientific_name",
    "totalNumber": "totalNumber",
    "totalWeightkg": "totalWeightkg",
}

GCS_NEARSHORE_SPECIMEN_MAP: dict[str, str] = {
    "Latitude": "latitude",
    "Longitude": "longitude",
    "datetime_UTC": "time",
    "itisTSN": "itis_tsn",
    "scientificName": "scientific_name",
    "standard_length": "standard_length",
    "fork_length": "fork_length",
}


def map_gcs_row(row: Mapping[str, Any], field_map: dict[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = dict(row)
    for gcs_key, erddap_key in field_map.items():
        if gcs_key in row and erddap_key not in out:
            out[erddap_key] = row[gcs_key]
    return out
