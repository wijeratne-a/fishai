"""Shared constants for CalCOFI CUFES ingestion."""

from __future__ import annotations

from typing import Final

SOURCE_ID: Final = "calcofi_cufes"

ERDDAP_TABLEDAP_BASE: Final = (
    "https://oceanview.pfeg.noaa.gov/erddap/tabledap/erdCalCOFIcufes"
)

ERDDAP_FIELDS: Final = (
    "cruise",
    "ship",
    "ship_code",
    "sample_number",
    "time",
    "latitude",
    "longitude",
    "start_temperature",
    "start_salinity",
    "start_wind_speed",
    "start_wind_direction",
    "start_pump_speed",
    "stop_time",
    "stop_latitude",
    "stop_longitude",
    "stop_temperature",
    "stop_salinity",
    "stop_wind_speed",
    "stop_wind_direction",
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

# Default sample duration bounds (minutes). CUFES underway samples are ~30 min;
# pilot distribution is mostly 20–45 min with rare shorter/longer segments.
DEFAULT_MIN_DURATION_MIN: Final = 10.0
DEFAULT_MAX_DURATION_MIN: Final = 90.0

# QC bitmask flags (samples with any flag set are dropped).
QC_MISSING_STOP_TIME: Final = 1 << 0
QC_REVERSED_TIME: Final = 1 << 1
QC_PUMP_INVALID: Final = 1 << 2
QC_COORD_INVALID: Final = 1 << 3
QC_DURATION_OUT_OF_RANGE: Final = 1 << 4
QC_INVALID_VOLUME: Final = 1 << 5

# Human-readable keys for ``cufes_qc_report.json`` (one counter per bit).
QC_RULE_LABELS: Final = (
    ("missing_stop_time", QC_MISSING_STOP_TIME),
    ("reversed_time", QC_REVERSED_TIME),
    ("pump_invalid", QC_PUMP_INVALID),
    ("coord_invalid", QC_COORD_INVALID),
    ("duration_out_of_range", QC_DURATION_OUT_OF_RANGE),
    ("invalid_volume", QC_INVALID_VOLUME),
)
