"""NWFSC FRAM West Coast groundfish bottom-trawl pelagic bycatch ingestion."""

from fishai.ingestion.biology.fram_groundfish_trawl.constants import SOURCE_ID
from fishai.ingestion.biology.fram_groundfish_trawl.fetch import (
    BBox,
    FramVariableDropError,
    build_selection_url,
    fetch_operation_hauls,
    fetch_pelagic_bycatch_catch,
    validate_response_variables,
)
from fishai.ingestion.biology.fram_groundfish_trawl.pipeline import sync_fram_groundfish_trawl
from fishai.ingestion.biology.fram_groundfish_trawl.trawl_id import survey_year_from_trawl_id
from fishai.ingestion.biology.fram_groundfish_trawl.transform import (
    TransformResult,
    format_qc_summary,
    make_tow_id,
    transform_rows,
)

__all__ = [
    "SOURCE_ID",
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
