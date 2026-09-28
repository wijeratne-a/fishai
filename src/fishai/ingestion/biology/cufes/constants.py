"""Shared constants for CalCOFI CUFES ingestion."""

from __future__ import annotations

from typing import Final

SOURCE_ID: Final = "calcofi_cufes"

ERDDAP_TABLEDAP_BASE: Final = (
    "https://oceanview.pfeg.noaa.gov/erddap/tabledap/erdCalCOFIcufes"
)

ERDDAP_FIELDS: Final = (
    "cruise",
    "ship_code",
    "sample_number",
    "time",
    "latitude",
    "longitude",
    "start_pump_speed",
    "stop_time",
    "stop_latitude",
    "stop_longitude",
    "stop_pump_speed",
    "sardine_eggs",
    "anchovy_eggs",
    "jack_mackerel_eggs",
    "hake_eggs",
    "squid_eggs",
    "other_fish_eggs",
)

# Wide egg columns → canonical taxon keys (exactly six categories).
EGG_CATEGORIES: Final = (
    ("sardine_eggs", "sardine"),
    ("anchovy_eggs", "anchovy"),
    ("jack_mackerel_eggs", "jack_mackerel"),
    ("hake_eggs", "hake"),
    ("squid_eggs", "squid"),
    ("other_fish_eggs", "other_fish"),
)

LIFE_STAGE_EGG: Final = "egg"
ZERO_SEMANTICS: Final = "EXPLICIT_ZERO"

# ERDDAP metadata (erdCalCOFIcufes.das): pump speed units are M^3 per minute.
PUMP_SPEED_UNITS: Final = "m^3/min"
# Plausible CUFES pump speeds (m³/min); ERDDAP logged max stop value 40.0 is out of range.
PUMP_SPEED_MIN_M3_PER_MIN: Final = 0.2
PUMP_SPEED_MAX_M3_PER_MIN: Final = 1.5
PUMP_SPEED_MAX_START_STOP_RATIO: Final = 2.0

# Duration bounds (minutes). Minimum depends on timestamp precision (see transform.duration_qc_flags).
DEFAULT_MAX_DURATION_MIN: Final = 90.0
SHORT_EVENT_THRESHOLD_MIN: Final = 10.0
MIN_DURATION_BOTH_SECONDS_NONZERO_MIN: Final = 2.0
MIN_DURATION_WHOLE_MINUTE_MIN: Final = 5.0

SPEED_REVIEW_THRESHOLD_KN: Final = 14.0

# QC bitmask flags (samples with any flag set are dropped).
QC_MISSING_STOP_TIME: Final = 1 << 0
QC_REVERSED_TIME: Final = 1 << 1
QC_PUMP_INVALID: Final = 1 << 2
QC_COORD_INVALID: Final = 1 << 3
QC_DURATION_OUT_OF_RANGE: Final = 1 << 4
QC_INVALID_VOLUME: Final = 1 << 5
QC_COUNT_INVALID: Final = 1 << 6
QC_KEY_INVALID: Final = 1 << 7
QC_NO_TAXA_SAMPLED: Final = 1 << 8
QC_DURATION_SHORT_SECOND: Final = 1 << 9
QC_DURATION_SHORT_MINUTE: Final = 1 << 10

# Human-readable keys for ``cufes_qc_report.json`` (one counter per bit).
QC_RULE_LABELS: Final = (
    ("missing_stop_time", QC_MISSING_STOP_TIME),
    ("reversed_time", QC_REVERSED_TIME),
    ("pump_invalid", QC_PUMP_INVALID),
    ("coord_invalid", QC_COORD_INVALID),
    ("duration_out_of_range", QC_DURATION_OUT_OF_RANGE),
    ("invalid_volume", QC_INVALID_VOLUME),
    ("count_invalid", QC_COUNT_INVALID),
    ("key_invalid", QC_KEY_INVALID),
    ("no_taxa_sampled", QC_NO_TAXA_SAMPLED),
    ("duration_short_second_precision", QC_DURATION_SHORT_SECOND),
    ("duration_short_minute_precision", QC_DURATION_SHORT_MINUTE),
)
