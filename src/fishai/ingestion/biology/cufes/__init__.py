"""CalCOFI CUFES ingestion implementation (subpackage; manifest module is ``calcofi_cufes``)."""

from fishai.ingestion.biology.cufes.constants import SOURCE_ID
from fishai.ingestion.biology.cufes.fetch import BBox, build_erddap_csv_url, fetch_cufes
from fishai.ingestion.biology.cufes.pipeline import format_qc_summary, sync_cufes
from fishai.ingestion.biology.cufes.transform import (
    TransformResult,
    make_event_id,
    qc_flags_for_row,
    transform_rows,
    volume_m3_for_row,
)

__all__ = [
    "SOURCE_ID",
    "BBox",
    "TransformResult",
    "build_erddap_csv_url",
    "fetch_cufes",
    "format_qc_summary",
    "make_event_id",
    "qc_flags_for_row",
    "sync_cufes",
    "transform_rows",
    "volume_m3_for_row",
]
