"""
Wind product qualification for the ``shared_forcing`` upwelling audit.

CUFES training covariates join on event mid-time. Bounds below match QC-kept events
from the PR #4 pilot ingest (``tests/fixtures/cufes_pilot_distances.csv`` →
``transform_rows``, 14,592 events): mid-time min 1996-03-16, max 2022-04-19 UTC.

ERDDAP metadata cited below was re-checked on 2026-09-28 (agent run); do not treat
as a substitute for live ``time_coverage_end`` before production pulls.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

WIND_AUDIT_VERIFIED_DATE = dt.date(2026, 9, 28)

# QC-kept CUFES event mid-time span used by ``build_cufes_training_covariates_table``.
CUFES_TRAINING_MID_TIME_MIN = dt.date(1996, 3, 16)
CUFES_TRAINING_MID_TIME_MAX = dt.date(2022, 4, 19)

# Wired ERDDAP product in ``sources/winds.py`` (not qualified for shared forcing alone).
CCMP_NRT_ERDDAP_ID = "ccmp-daily-v2-1-NRT"
CCMP_NRT_PRODUCT_VERSION = "v2.1"
# https://oceanwatch.pifsc.noaa.gov/erddap/info/ccmp-daily-v2-1-NRT/index.html
CCMP_NRT_COVERAGE_START = dt.date(2015, 1, 16)
CCMP_NRT_COVERAGE_END_DOCUMENTED = dt.date(2026, 9, 26)

NCEI_BLENDED_SCIENCE_ERDDAP_ID = "noaacwBlendedWindsDaily"
NCEI_BLENDED_SCIENCE_VERSION = "V2.0"
# https://coastwatch.noaa.gov/erddap/info/noaacwBlendedWindsDaily/index.html
NCEI_BLENDED_SCIENCE_COVERAGE_START = dt.date(1987, 7, 9)
NCEI_BLENDED_SCIENCE_COVERAGE_END_DOCUMENTED = dt.date(2026, 8, 31)

NCEI_BLENDED_NRT_ERDDAP_ID = "noaacwBlendednrtWindsDaily"
# https://coastwatch.noaa.gov/erddap/info/noaacwBlendednrtWindsDaily/index.html
NCEI_BLENDED_NRT_COVERAGE_START = dt.date(2023, 1, 1)
NCEI_BLENDED_NRT_COVERAGE_END_DOCUMENTED = dt.date(2023, 3, 5)

ASCAT_DAILY_ERDDAP_ID = "erdQMwind1day"
# https://coastwatch.pfeg.noaa.gov/erddap/info/erdQMwind1day/index.html
ASCAT_DAILY_COVERAGE_START = dt.date(2013, 8, 27)
ASCAT_DAILY_COVERAGE_END_DOCUMENTED = dt.date(2022, 12, 31)

CCMP_V20_ERDDAP_ID = "ccmp-daily-v2-0"
CCMP_V20_PRODUCT_VERSION = "v2.0"
CCMP_V20_COVERAGE_START = dt.date(1987, 7, 10)
CCMP_V20_COVERAGE_END = dt.date(2019, 4, 29)

CCMP_V31_PODAAC_ID = "CCMP_WINDS_10M6HR_L4_V3.1"

# Auditor conclusion: no one product spans training + daily nowcast for this CUFES table.
UPWELLING_SHARED_FORCING_QUALIFIED = False

# When false, training table writes NaN ``upwelling`` and ``upwelling_status`` (no wind ERDDAP pulls).
UPWELLING_WIND_FORCING_ENABLED = False
UPWELLING_STATUS_NO_CONSISTENT_WIND = "no_consistent_wind_product"


def wind_product_audit_summary() -> dict[str, Any]:
    """Structured candidate list for PR / parquet metadata."""
    return {
        "audit_verified_date": WIND_AUDIT_VERIFIED_DATE.isoformat(),
        "cufes_training_mid_time_min": CUFES_TRAINING_MID_TIME_MIN.isoformat(),
        "cufes_training_mid_time_max": CUFES_TRAINING_MID_TIME_MAX.isoformat(),
        "shared_forcing_qualified": UPWELLING_SHARED_FORCING_QUALIFIED,
        "candidates": [
            {
                "product": "NOAA NCEI Blended Sea Winds V2.0 science quality (daily)",
                "dataset_id": NCEI_BLENDED_SCIENCE_ERDDAP_ID,
                "product_version": NCEI_BLENDED_SCIENCE_VERSION,
                "coverage_start": NCEI_BLENDED_SCIENCE_COVERAGE_START.isoformat(),
                "coverage_end": NCEI_BLENDED_SCIENCE_COVERAGE_END_DOCUMENTED.isoformat(),
                "latency": (
                    "~28 days behind real time on 2026-09-28 "
                    "(ERDDAP time_coverage_end 2026-08-31; summary: quasi-daily updates)"
                ),
                "daily_nowcast": False,
                "ndbc_buoy_assimilation": False,
                "source": (
                    "CoastWatch ERDDAP noaacwBlendedWindsDaily: satellite OA + "
                    "ERA5 wind direction (source attribute); license requires citation"
                ),
            },
            {
                "product": "NOAA NCEI Blended Sea Winds V2.0 NRT (daily, CoastWatch ERDDAP)",
                "dataset_id": NCEI_BLENDED_NRT_ERDDAP_ID,
                "product_version": NCEI_BLENDED_SCIENCE_VERSION,
                "coverage_start": NCEI_BLENDED_NRT_COVERAGE_START.isoformat(),
                "coverage_end": NCEI_BLENDED_NRT_COVERAGE_END_DOCUMENTED.isoformat(),
                "latency": "Stalled: date_modified 2023-03-06; not operational on ERDDAP",
                "daily_nowcast": False,
                "ndbc_buoy_assimilation": False,
                "source": (
                    "CoastWatch ERDDAP noaacwBlendednrtWindsDaily (GFS0.25 direction per "
                    "acknowledgement). NCEI DOI 10.25921/mxt4-b075 lists THREDDS/direct "
                    "download for NRT; no active ERDDAP NRT mirror found in CoastWatch search "
                    "beyond this stalled dataset (2026-09-28)."
                ),
            },
            {
                "product": "RSS CCMP V2.1 NRT (6-hour; daily aggregate on OceanWatch ERDDAP)",
                "dataset_id": CCMP_NRT_ERDDAP_ID,
                "product_version": CCMP_NRT_PRODUCT_VERSION,
                "coverage_start": CCMP_NRT_COVERAGE_START.isoformat(),
                "coverage_end": CCMP_NRT_COVERAGE_END_DOCUMENTED.isoformat(),
                "latency": "~48 h routine NRT (Mears et al. 2019); 6-hourly native timestep",
                "daily_nowcast": True,
                "ndbc_buoy_assimilation": False,
                "source": (
                    "OceanWatch ERDDAP summary: NO buoy data; NCEP GFS 0.25° background"
                ),
            },
            {
                "product": "RSS CCMP V2.0 reanalysis (6-hour)",
                "dataset_id": CCMP_V20_ERDDAP_ID,
                "product_version": CCMP_V20_PRODUCT_VERSION,
                "coverage_start": CCMP_V20_COVERAGE_START.isoformat(),
                "coverage_end": CCMP_V20_COVERAGE_END.isoformat(),
                "latency": "Reanalysis (ERA-Interim background); not nowcast",
                "daily_nowcast": False,
                "ndbc_buoy_assimilation": True,
                "source": "OceanWatch ERDDAP ccmp-daily-v2-0 summary (NDBC/PMEL/ISDM buoys)",
            },
            {
                "product": "RSS CCMP V3.1 L4 (6-hourly; PO.DAAC / RSS HTTPS)",
                "dataset_id": CCMP_V31_PODAAC_ID,
                "product_version": "3.1",
                "coverage_start": "1993-01-01",
                "coverage_end": "present (rolling; not same-day nowcast)",
                "latency": "2–3 months for new files (PO.DAAC dataset description)",
                "daily_nowcast": False,
                "ndbc_buoy_assimilation": False,
                "source": (
                    "PO.DAAC CCMP_WINDS_10M6HR_L4_V3.1; RSS CCMP page: V3.1 vs CCMP-NRT "
                    "must not be mixed; no CCMP v3 ERDDAP match on CoastWatch search "
                    "(2026-09-28)"
                ),
            },
            {
                "product": "CoastWatch Metop ASCAT daily composite",
                "dataset_id": ASCAT_DAILY_ERDDAP_ID,
                "product_version": "NRT composite",
                "coverage_start": ASCAT_DAILY_COVERAGE_START.isoformat(),
                "coverage_end": ASCAT_DAILY_COVERAGE_END_DOCUMENTED.isoformat(),
                "latency": "Stopped updating (ERDDAP end 2022-12-31)",
                "daily_nowcast": False,
                "ndbc_buoy_assimilation": False,
                "source": "coastwatch.pfeg ERDDAP erdQMwind1day metadata",
            },
        ],
        "gap_notes": (
            "Training needs 1996-03-16 through 2022-04-19. NCEI Blended V2.0 science ERDDAP "
            "covers the full training span but lags ~1 month (not daily nowcast). Its CoastWatch "
            "NRT ERDDAP companion is frozen at 2023-03-05. CCMP V2.1 NRT is current for nowcast "
            "but starts 2015-01-16. CCMP V3.1 is research latency (~months), not daily NRT on "
            "ERDDAP. Mixing science + NRT or CCMP generations is explicitly disallowed."
        ),
    }


def require_day_within_ccmp_nrt(day: dt.date) -> None:
    """Reject training/hindcast days outside CCMP NRT ERDDAP coverage (no silent product mix)."""
    if day < CCMP_NRT_COVERAGE_START:
        raise ValueError(
            f"wind day {day.isoformat()} precedes {CCMP_NRT_ERDDAP_ID} "
            f"(coverage starts {CCMP_NRT_COVERAGE_START.isoformat()})"
        )
