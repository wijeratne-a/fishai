"""Shared constants for SWFSC CPS nearshore set catch ingestion."""

from __future__ import annotations

from typing import Final

from fishai.ingestion.biology.cps_trawl.constants import (
    ITIS_TSN_ENGRAULIS_MORDAX,
    ITIS_TSN_SARDINOPS_SAGAX,
)

SOURCE_ID: Final = "swfsc_cps_nearshore_set_catch"

ERDDAP_TABLEDAP_BASE: Final = (
    "https://coastwatch.pfeg.noaa.gov/erddap/tabledap/FRDCPSNearshoreSetCatch"
)

ERDDAP_FIELDS: Final = (
    "cruise",
    "ship",
    "date",
    "time_PDT",
    "time",
    "set",
    "latitude",
    "longitude",
    "state",
    "gearType",
    "itis_tsn",
    "scientific_name",
    "totalNumber",
    "totalWeightkg",
)

# Pilot species matrix targets (adult/juvenile encounter evidence).
PILOT_MATRIX_SPECIES: Final = ("Sardinops sagax", "Engraulis mordax")
PILOT_SPECIES_ITIS_TSN: Final = {
    "Sardinops sagax": ITIS_TSN_SARDINOPS_SAGAX,
    "Engraulis mordax": ITIS_TSN_ENGRAULIS_MORDAX,
}
SET_SPECIES_MATRIX_FILENAME: Final = "cps_nearshore_set_species_matrix.parquet"

# Zero-catch expansion gate (per-cruise evidence in
# config/cps_nearshore_zero_frame_evidence.yaml).
ZERO_FRAME_UNVERIFIED_REASON: Final = "zero_frame_unverified"
SET_META_MISSING_REASON: Final = "set_meta_missing"
UNRESOLVED_HIGHER_TAXON_REASON: Final = "unresolved_higher_taxon"
UNPARSEABLE_CATCH_ROW_REASON: Final = "unparseable_catch_row"

# QC bitmask flags (sets with any flag set are dropped from outputs).
QC_KEY_INVALID: Final = 1 << 0
QC_COORD_INVALID: Final = 1 << 1
QC_TIME_INVALID: Final = 1 << 2
QC_SET_METADATA_CONFLICT: Final = 1 << 3
QC_CATCH_INVALID: Final = 1 << 4

QC_RULE_LABELS: Final = (
    ("key_invalid", QC_KEY_INVALID),
    ("coord_invalid", QC_COORD_INVALID),
    ("time_invalid", QC_TIME_INVALID),
    ("set_metadata_conflict", QC_SET_METADATA_CONFLICT),
    ("catch_invalid", QC_CATCH_INVALID),
)

# Purse-seine sets are point events; no tow duration/distance applies.
# Kept explicit so downstream effort joins fail closed instead of guessing.
EFFORT_DURATION_NULL_REASON: Final = "not_applicable_purse_seine_set"
