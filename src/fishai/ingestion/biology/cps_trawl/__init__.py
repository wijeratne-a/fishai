"""SWFSC CPS trawl haul catch ingestion (subpackage; manifest module is ``swfsc_cps_trawl_haul_catch``)."""

from fishai.ingestion.biology.cps_trawl.constants import SOURCE_ID
from fishai.ingestion.biology.cps_trawl.fetch import BBox, build_erddap_csv_url, fetch_cps_trawl_haul_catch
from fishai.ingestion.biology.cps_trawl.matrix import ZeroFrameUnverifiedError, expand_haul_species_matrix
from fishai.ingestion.biology.cps_trawl.pipeline import format_qc_summary, sync_cps_trawl_haul_catch
from fishai.ingestion.biology.cps_trawl.transform import TransformResult, make_haul_id, transform_rows

__all__ = [
    "SOURCE_ID",
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
