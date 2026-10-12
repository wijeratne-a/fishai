"""SWFSC CPS nearshore set catch via ERDDAP ``FRDCPSNearshoreSetCatch``.

Purse-seine set catch weights and counts from the nearshore portion of the
SWFSC-FRD fishery-independent coastal pelagic species survey (2019–present
on ERDDAP). Processed tables:

- ``cps_nearshore_sets.parquet`` — one row per purse-seine set
  (``set_id`` = ``CPSNearshore:{cruise}:{ship}:{set}``)
- ``cps_nearshore_catch.parquet`` — long catch by species (no implied zeros
  without per-cruise evidence YAML)
- ``cps_nearshore_set_species_matrix.parquet`` — set × pilot-species
  encounter matrix (1 = observed, 0 = implied zero in verified frame,
  null = not available)

Sets are point events: no tow duration or distance applies; effort columns
are explicit nulls with reasons. License on ERDDAP: NOAA free-use
disclaimer; see ``data/SOURCES.yaml`` ``license_text``.
"""

from __future__ import annotations

from fishai.ingestion.biology.cps_nearshore import (
    SOURCE_ID,
    BBox,
    TransformResult,
    ZeroFrameUnverifiedError,
    build_erddap_csv_url,
    catch_row_invalid,
    expand_set_species_matrix,
    fetch_cps_nearshore_set_catch,
    format_qc_summary,
    iter_yearly_windows,
    load_zero_frame_evidence,
    make_set_id,
    parse_catch_row,
    read_cps_nearshore_csv,
    sync_cps_nearshore_set_catch,
    transform_rows,
)

SOURCE_MODULE = "swfsc_cps_nearshore_set_catch"

__all__ = [
    "SOURCE_ID",
    "SOURCE_MODULE",
    "BBox",
    "TransformResult",
    "ZeroFrameUnverifiedError",
    "build_erddap_csv_url",
    "catch_row_invalid",
    "expand_set_species_matrix",
    "fetch_cps_nearshore_set_catch",
    "format_qc_summary",
    "iter_yearly_windows",
    "load_zero_frame_evidence",
    "make_set_id",
    "parse_catch_row",
    "read_cps_nearshore_csv",
    "sync_cps_nearshore_set_catch",
    "transform_rows",
]
