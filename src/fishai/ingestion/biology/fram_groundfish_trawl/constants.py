"""Shared constants for NWFSC FRAM West Coast groundfish bottom-trawl ingestion."""

from __future__ import annotations

from typing import Final

from fishai.ingestion.biology.cps_trawl.constants import (
    ITIS_TSN_ENGRAULIS_MORDAX,
    ITIS_TSN_SARDINOPS_SAGAX,
)

SOURCE_ID: Final = "nwfsc_fram_groundfish_trawl"

# Working API base (legacy www.nwfsc.noaa.gov/data/api serves an app shell).
API_BASE: Final = "https://www.webapps.nwfsc.noaa.gov/trips/api/v1/source"

CATCH_LAYER: Final = "trawl.catch_fact"
HAUL_LAYER: Final = "trawl.operation_haul_fact"

# West Coast Groundfish Bottom Trawl Survey (2003–present on FRAM).
GROUNDFISH_COMBO_PROJECT: Final = "Groundfish Slope and Shelf Combination Survey"

# Adult corroboration targets: pelagic bycatch on bottom-trawl tows only (presence rows).
TARGET_SPECIES: Final = ("Sardinops sagax", "Engraulis mordax")
TARGET_SPECIES_ITIS_TSN: Final = {
    "Sardinops sagax": ITIS_TSN_SARDINOPS_SAGAX,
    "Engraulis mordax": ITIS_TSN_ENGRAULIS_MORDAX,
}

SCIENTIFIC_NAME_FIELD: Final = "field_identified_taxonomy_dim$scientific_name"

CATCH_VARIABLES: Final = (
    "trawl_id",
    SCIENTIFIC_NAME_FIELD,
    "vessel",
    "tow",
    "project",
    "performance",
    "total_catch_wt_kg",
    "total_catch_numbers",
    "cpue_kg_per_ha_der",
    "depth_m",
    "station_invalid",
)

HAUL_VARIABLES: Final = (
    "trawl_id",
    "vessel",
    "tow",
    "project",
    "performance",
    "datetime_utc_iso",
    "area_swept_ha_der",
    "latitude_dd",
    "longitude_dd",
    "gear_start_latitude_dd",
    "gear_start_longitude_dd",
    "gear_end_latitude_dd",
    "gear_end_longitude_dd",
    "depth_hi_prec_m",
    "sampling_start_hhmmss",
    "sampling_end_hhmmss",
    "station_invalid",
)

# Pelagic sardine/anchovy on bottom-trawl gear: corroborating presence-only bycatch, not
# a standardized pelagic survey frame — never expand implied zeros for training.
PELAGIC_BYCATCH_BIAS_NOTE: Final = (
    "Bottom-trawl survey targets groundfish; sardine/anchovy appear only as incidental "
    "pelagic bycatch. Use as adult corroboration only, not primary presence-absence."
)
PRESENCE_ONLY_BYCATCH_REASON: Final = "pelagic_bycatch_presence_only"

QC_TRAWL_ID_INVALID: Final = 1 << 0
QC_SPECIES_INVALID: Final = 1 << 1
QC_HAUL_JOIN_MISSING: Final = 1 << 2
QC_COORD_INVALID: Final = 1 << 3
QC_PERFORMANCE_EXCLUDED: Final = 1 << 4
QC_YEAR_MISMATCH: Final = 1 << 5
QC_CPUE_MISSING: Final = 1 << 6

QC_RULE_LABELS: Final = (
    ("trawl_id_invalid", QC_TRAWL_ID_INVALID),
    ("species_invalid", QC_SPECIES_INVALID),
    ("haul_join_missing", QC_HAUL_JOIN_MISSING),
    ("coord_invalid", QC_COORD_INVALID),
    ("performance_excluded", QC_PERFORMANCE_EXCLUDED),
    ("year_mismatch", QC_YEAR_MISMATCH),
    ("cpue_missing", QC_CPUE_MISSING),
)
