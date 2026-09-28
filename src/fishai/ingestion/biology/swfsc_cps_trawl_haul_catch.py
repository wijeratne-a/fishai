"""SWFSC CPS trawl haul catch via ERDDAP ``FRDCPSTrawlLHHaulCatch``.

Mid-water surface trawl catch weights and counts from DEPM, acoustic-trawl (ATM), and
SaKe surveys (2003–present on ERDDAP). Processed tables:

- ``cps_trawl_hauls.parquet`` — one row per tow (``haul_id`` = ``CPSTrawl:{cruise}:{ship}:{haul}``)
- ``cps_trawl_catch.parquet`` — long catch by species (no implied zeros without per-cruise evidence YAML)

Net mouth area is not in the source dataset; effort columns are explicit nulls with reasons.
License on ERDDAP: NOAA free-use disclaimer; see ``data/SOURCES.yaml`` ``license_text``.
"""

from __future__ import annotations

from fishai.ingestion.biology.cps_trawl import (
    SOURCE_ID,
    BBox,
    TransformResult,
    ZeroFrameUnverifiedError,
    build_erddap_csv_url,
    expand_haul_species_matrix,
    fetch_cps_trawl_haul_catch,
    format_qc_summary,
    make_haul_id,
    sync_cps_trawl_haul_catch,
    transform_rows,
)

SOURCE_MODULE = "swfsc_cps_trawl_haul_catch"

__all__ = [
    "SOURCE_ID",
    "SOURCE_MODULE",
    "BBox",
    "TransformResult",
    "ZeroFrameUnverifiedError",
    "build_erddap_csv_url",
    "expand_haul_species_matrix",
    "fetch_cps_trawl_haul_catch",
    "format_qc_summary",
    "make_haul_id",
    "sync_cps_trawl_haul_catch",
    "transform_rows",
]
