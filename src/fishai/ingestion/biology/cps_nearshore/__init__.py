"""SWFSC CPS nearshore purse-seine set catch ingestion.

Row-level (set-level) catch of coastal pelagic species from the nearshore
portion of the SWFSC Fisheries Resources Division fishery-independent CPS
survey, served on NOAA CoastWatch ERDDAP as ``FRDCPSNearshoreSetCatch``.

This is adult/juvenile evidence with survey effort (purse-seine sets):
sets are the sampling frame, so a set with no recorded catch of a target
species is a candidate absence — but implied zeros are only emitted for
sets in a per-cruise verified frame (see ``zero_frame.py`` and
``config/cps_nearshore_zero_frame_evidence.yaml``), never silently.
"""

from __future__ import annotations

from fishai.ingestion.biology.cps_nearshore.catch import (
    catch_row_invalid,
    parse_catch_row,
)
from fishai.ingestion.biology.cps_nearshore.constants import (
    SOURCE_ID,
    PILOT_MATRIX_SPECIES,
    PILOT_SPECIES_ITIS_TSN,
    SET_SPECIES_MATRIX_FILENAME,
)
from fishai.ingestion.biology.cps_nearshore.fetch import (
    BBox,
    build_erddap_csv_url,
    fetch_cps_nearshore_set_catch,
    iter_yearly_windows,
    read_cps_nearshore_csv,
)
from fishai.ingestion.biology.cps_nearshore.matrix import (
    ZeroFrameUnverifiedError,
    expand_set_species_matrix,
)
from fishai.ingestion.biology.cps_nearshore.pipeline import (
    sync_cps_nearshore_set_catch,
)
from fishai.ingestion.biology.cps_nearshore.transform import (
    TransformResult,
    format_qc_summary,
    make_set_id,
    transform_rows,
)
from fishai.ingestion.biology.cps_nearshore.zero_frame import (
    load_zero_frame_evidence,
)

__all__ = [
    "SOURCE_ID",
    "PILOT_MATRIX_SPECIES",
    "PILOT_SPECIES_ITIS_TSN",
    "SET_SPECIES_MATRIX_FILENAME",
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
