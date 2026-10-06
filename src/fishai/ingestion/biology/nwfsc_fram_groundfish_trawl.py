"""NWFSC FRAM West Coast Groundfish Bottom Trawl Survey (pelagic bycatch corroboration).

Tow-level sardine and anchovy catch with haul effort metadata and CPUE per hectare from the
FRAM Data Warehouse (2003–present). API base:
``https://www.webapps.nwfsc.noaa.gov/trips/api/v1/source/`` (not the legacy ``/data/api`` shell).

Pelagic bycatch on bottom-trawl gear is a corroborating adult source only — not a primary
presence-absence frame. Catch rows are presence-only; implied zeros are never emitted.
License: U.S. Federal public domain / NOAA Fisheries; see ``data/SOURCES.yaml``.
"""

from __future__ import annotations

from fishai.ingestion.biology.fram_groundfish_trawl import (
    SOURCE_ID,
    BBox,
    FramVariableDropError,
    TransformResult,
    build_selection_url,
    fetch_operation_hauls,
    fetch_pelagic_bycatch_catch,
    format_qc_summary,
    make_tow_id,
    survey_year_from_trawl_id,
    sync_fram_groundfish_trawl,
    transform_rows,
    validate_response_variables,
)

SOURCE_MODULE = "nwfsc_fram_groundfish_trawl"

__all__ = [
    "SOURCE_ID",
    "SOURCE_MODULE",
    "BBox",
    "FramVariableDropError",
    "TransformResult",
    "build_selection_url",
    "fetch_operation_hauls",
    "fetch_pelagic_bycatch_catch",
    "format_qc_summary",
    "make_tow_id",
    "survey_year_from_trawl_id",
    "sync_fram_groundfish_trawl",
    "transform_rows",
    "validate_response_variables",
]
