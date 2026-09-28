"""Shared constants for SWFSC CPS trawl haul catch ingestion."""

from __future__ import annotations

from typing import Final

SOURCE_ID: Final = "swfsc_cps_trawl_haul_catch"

ERDDAP_TABLEDAP_BASE: Final = (
    "https://oceanview.pfeg.noaa.gov/erddap/tabledap/FRDCPSTrawlLHHaulCatch"
)

ERDDAP_FIELDS: Final = (
    "cruise",
    "ship",
    "haul",
    "collection",
    "latitude",
    "longitude",
    "stop_latitude",
    "stop_longitude",
    "time",
    "haulback_time",
    "surface_temp",
    "surface_temp_method",
    "ship_spd_through_water",
    "itis_tsn",
    "scientific_name",
    "subsample_count",
    "subsample_weight",
    "remaining_weight",
    "presence_only",
)

# Zero-catch expansion gate (per-cruise evidence in config/cps_trawl_zero_frame_evidence.yaml).
ZERO_FRAME_UNVERIFIED_REASON: Final = "zero_frame_unverified"
ANIMALIA_ONLY_ZERO_FRAME_REASON: Final = "animalia_only_undocumented"
HAUL_META_MISSING_REASON: Final = "haul_meta_missing"
UNRESOLVED_HIGHER_TAXON_REASON: Final = "unresolved_higher_taxon"
UNPARSEABLE_CATCH_ROW_REASON: Final = "unparseable_catch_row"
WEIGHT_FLAG_PARTIAL: Final = "weight_partial"

# Effort fields not present in FRDCPSTrawlLHHaulCatch.
NET_MOUTH_AREA_NULL_REASON: Final = "not_in_source_dataset"

# Tow duration QC (minutes).
MIN_TOW_DURATION_MIN: Final = 0.5
MAX_TOW_DURATION_MIN: Final = 180.0

# QC bitmask flags (hauls with any flag set are dropped from outputs).
QC_KEY_INVALID: Final = 1 << 0
QC_COORD_INVALID: Final = 1 << 1
QC_TIME_INVALID: Final = 1 << 2
QC_DURATION_INVALID: Final = 1 << 3
QC_HAUL_METADATA_CONFLICT: Final = 1 << 4
QC_CATCH_INVALID: Final = 1 << 5

QC_RULE_LABELS: Final = (
    ("key_invalid", QC_KEY_INVALID),
    ("coord_invalid", QC_COORD_INVALID),
    ("time_invalid", QC_TIME_INVALID),
    ("duration_invalid", QC_DURATION_INVALID),
    ("haul_metadata_conflict", QC_HAUL_METADATA_CONFLICT),
    ("catch_invalid", QC_CATCH_INVALID),
)
