"""
Wind product qualification for the ``shared_forcing`` upwelling audit.

CUFES training covariates join on event mid-time. Bounds below match QC-kept events
from the PR #4 pilot ingest (``tests/fixtures/cufes_pilot_distances.csv`` →
``transform_rows``, 14,592 events): mid-time min 1996-03-16, max 2022-04-19 UTC.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

# QC-kept CUFES event mid-time span used by ``build_cufes_training_covariates_table``.
CUFES_TRAINING_MID_TIME_MIN = dt.date(1996, 3, 16)
CUFES_TRAINING_MID_TIME_MAX = dt.date(2022, 4, 19)

# Wired ERDDAP product in ``sources/winds.py`` (not qualified for shared forcing alone).
CCMP_NRT_ERDDAP_ID = "ccmp-daily-v2-1-NRT"
CCMP_NRT_PRODUCT_VERSION = "v2.1"

# NOAA OceanWatch ERDDAP ``time_coverage_start`` / ``time_coverage_end`` (verified 2026-09-28).
# https://oceanwatch.pifsc.noaa.gov/erddap/info/ccmp-daily-v2-1-NRT/index.html
CCMP_NRT_COVERAGE_START = dt.date(2015, 1, 16)
CCMP_NRT_COVERAGE_END_DOCUMENTED = dt.date(2026, 9, 26)

# CCMP V2.0 reanalysis on OceanWatch (not NRT).
# https://oceanwatch.pifsc.noaa.gov/erddap/info/ccmp-daily-v2-0/index.html
CCMP_V20_ERDDAP_ID = "ccmp-daily-v2-0"
CCMP_V20_PRODUCT_VERSION = "v2.0"
CCMP_V20_COVERAGE_START = dt.date(1987, 7, 10)
CCMP_V20_COVERAGE_END = dt.date(2019, 4, 29)

# PacIOOS NCEP GFS ERDDAP (nowcast-oriented; short archive on this mirror).
# https://pae-paha.pacioos.hawaii.edu/erddap/info/ncep_global/index.html
NCEP_GLOBAL_ERDDAP_ID = "ncep_global"
NCEP_GLOBAL_COVERAGE_START = dt.date(2022, 12, 1)

# Auditor conclusion: no one product spans training + daily nowcast for this CUFES table.
UPWELLING_SHARED_FORCING_QUALIFIED = False


def wind_product_audit_summary() -> dict[str, Any]:
    """Structured candidate list for PR / parquet metadata (sources cited in module docstring)."""
    return {
        "cufes_training_mid_time_min": CUFES_TRAINING_MID_TIME_MIN.isoformat(),
        "cufes_training_mid_time_max": CUFES_TRAINING_MID_TIME_MAX.isoformat(),
        "shared_forcing_qualified": UPWELLING_SHARED_FORCING_QUALIFIED,
        "candidates": [
            {
                "product": "RSS CCMP V2.1 Near-Real-Time (6-hour, daily ERDDAP aggregate)",
                "dataset_id": CCMP_NRT_ERDDAP_ID,
                "product_version": CCMP_NRT_PRODUCT_VERSION,
                "coverage_start": CCMP_NRT_COVERAGE_START.isoformat(),
                "coverage_end": CCMP_NRT_COVERAGE_END_DOCUMENTED.isoformat(),
                "latency": "~48 h (Mears et al. 2019, JGR Oceans; ERDDAP NRT stream)",
                "ndbc_buoy_assimilation": False,
                "source": "ERDDAP summary attribute on ccmp-daily-v2-1-NRT (NO buoy data)",
            },
            {
                "product": "RSS CCMP V2.0 reanalysis (6-hour)",
                "dataset_id": CCMP_V20_ERDDAP_ID,
                "product_version": CCMP_V20_PRODUCT_VERSION,
                "coverage_start": CCMP_V20_COVERAGE_START.isoformat(),
                "coverage_end": CCMP_V20_COVERAGE_END.isoformat(),
                "latency": "Reanalysis (not daily nowcast)",
                "ndbc_buoy_assimilation": True,
                "source": "ERDDAP summary on ccmp-daily-v2-0 (NDBC/PMEL/ISDM buoys)",
            },
            {
                "product": "NCEP GFS 0.5° (PacIOOS ncep_global)",
                "dataset_id": NCEP_GLOBAL_ERDDAP_ID,
                "product_version": "operational GFS FMRC best",
                "coverage_start": NCEP_GLOBAL_COVERAGE_START.isoformat(),
                "coverage_end": "rolling (ERDDAP time_coverage_end; 8-day forecast window)",
                "latency": "3-hourly steps; testOutOfDate now+136hours on ERDDAP",
                "ndbc_buoy_assimilation": False,
                "source": "PacIOOS ERDDAP ncep_global metadata (model analysis/forecast)",
            },
        ],
        "gap_notes": (
            "Training needs winds from 1996-03-16 through 2022-04-19; CCMP V2.1 NRT begins "
            "2015-01-16. CCMP V2.0 ends 2019-04-29 and is not a nowcast stream. "
            "PacIOOS ncep_global archive starts 2022-12-01. No single listed product covers "
            "full training and daily operational nowcast."
        ),
    }


def require_day_within_ccmp_nrt(day: dt.date) -> None:
    """Reject training/hindcast days outside CCMP NRT ERDDAP coverage (no silent product mix)."""
    if day < CCMP_NRT_COVERAGE_START:
        raise ValueError(
            f"wind day {day.isoformat()} precedes {CCMP_NRT_ERDDAP_ID} "
            f"(coverage starts {CCMP_NRT_COVERAGE_START.isoformat()})"
        )
