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

# L50 standard-length cutoffs (science-reviewed; see docs/adult-training-table-validation.md).
ADULT_MIN_LENGTH_MM: Final = {
    "Sardinops sagax": 160.0,
    "Engraulis mordax": 98.0,
    # L50 from Fitch (1956): 50% female maturity at 250 mm fork length (100% at 350 mm).
    # Cutoff applied to standard length when measured; fork length only when SL absent
    # (published L50 in fork length — see docs/adult-jack-mackerel-model-readout.md).
    "Trachurus symmetricus": 250.0,
}

ADULT_LENGTH_CUTOFF_DISCLOSURE: Final = (
    "Adult specimens were retained only if standard length >= 250 mm (jack mackerel, "
    "Trachurus symmetricus). This cutoff is the length at 50% maturity (L50) from "
    "Fitch (1956): 50% of females mature at 250 mm fork length (100% at 350 mm). "
    "The published value is in fork length; applied to standard length it is "
    "conservative, since fork length exceeds standard length for the same fish."
)

EVIDENCE_IMPLIED_ZERO: Final = "implied_zero_enumerated_frame"

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
    "absence_evidence",
)
