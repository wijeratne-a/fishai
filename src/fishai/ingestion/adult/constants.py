"""Adult CPS training-table paths and adult length cutoffs."""

from __future__ import annotations

from typing import Final

from fishai.ingestion.biology.cps_trawl.constants import PILOT_MATRIX_SPECIES
from fishai.ingestion.sources import REPO_ROOT

DEFAULT_PROCESSED_DIR: Final = REPO_ROOT / "data" / "processed" / "adult_cps"

DEFAULT_EVENTS_PATH: Final = DEFAULT_PROCESSED_DIR / "adult_cps_events.parquet"
DEFAULT_TRAINING_TABLE_PATH: Final = DEFAULT_PROCESSED_DIR / "adult_cps_training_table.parquet"
DEFAULT_DROPS_PATH: Final = DEFAULT_PROCESSED_DIR / "adult_cps_training_covariate_drops.parquet"
DEFAULT_DROP_SUMMARY_PATH: Final = (
    DEFAULT_PROCESSED_DIR / "adult_cps_training_covariate_drop_summary.json"
)
DEFAULT_BUILD_SUMMARY_PATH: Final = DEFAULT_PROCESSED_DIR / "adult_cps_build_summary.json"

TRAWL_HAULS_PATH: Final = (
    REPO_ROOT / "data" / "processed" / "swfsc_cps_trawl_haul_catch" / "cps_trawl_hauls.parquet"
)
TRAWL_CATCH_PATH: Final = (
    REPO_ROOT / "data" / "processed" / "swfsc_cps_trawl_haul_catch" / "cps_trawl_catch.parquet"
)
TRAWL_SPECIMENS_PATH: Final = (
    REPO_ROOT
    / "data"
    / "processed"
    / "swfsc_cps_trawl_haul_catch"
    / "cps_trawl_specimens.parquet"
)

NEARSHORE_SETS_PATH: Final = (
    REPO_ROOT
    / "data"
    / "processed"
    / "swfsc_cps_nearshore_set_catch"
    / "cps_nearshore_sets.parquet"
)
NEARSHORE_CATCH_PATH: Final = (
    REPO_ROOT
    / "data"
    / "processed"
    / "swfsc_cps_nearshore_set_catch"
    / "cps_nearshore_catch.parquet"
)
NEARSHORE_SPECIMENS_PATH: Final = (
    REPO_ROOT
    / "data"
    / "processed"
    / "swfsc_cps_nearshore_set_catch"
    / "cps_nearshore_specimens.parquet"
)

OBSERVATION_SOURCE_TRAWL: Final = "swfsc_cps_trawl_haul_catch"
OBSERVATION_SOURCE_NEARSHORE: Final = "swfsc_cps_nearshore_set_catch"

# Median adult sizes in validation (sardine 160 mm, anchovy 106 mm). Cutoffs exclude
# juveniles while retaining adult-dominated catches (median length must meet cutoff).
ADULT_MIN_LENGTH_MM: Final = {
    "Sardinops sagax": 120.0,
    "Engraulis mordax": 70.0,
}

PILOT_SPECIES: Final = tuple(PILOT_MATRIX_SPECIES)

EXCLUDE_REASON_PRESENCE_ONLY: Final = "presence_only"
EXCLUDE_REASON_JUVENILE: Final = "juvenile_median_length"
EXCLUDE_REASON_NO_SPECIMEN: Final = "no_specimen_length_evidence"
EXCLUDE_REASON_OUTSIDE_PILOT: Final = "outside_pilot_bbox"

TRAINING_TABLE_EXTRA_COLUMNS: Final = (
    "species",
    "observation_source",
    "encounter",
    "weight_kg",
    "count_observed",
    "effort_duration_min",
    "effort_duration_null_reason",
    "adult_median_length_mm",
    "biology_excluded",
    "biology_excluded_reason",
)
