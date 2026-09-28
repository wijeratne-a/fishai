"""CalCOFI CUFES egg counts via ERDDAP ``erdCalCOFIcufes``.

Pump speed units (ERDDAP ``erdCalCOFIcufes.das``): ``M^3 per minute`` — effort volume is
mean(start/stop pump speed) × sample duration in minutes, yielding m³.

License on ERDDAP (not CC-BY): NOAA free-use disclaimer; see ``data/SOURCES.yaml``.
"""

from __future__ import annotations

from fishai.ingestion.biology.cufes_constants import SOURCE_ID
from fishai.ingestion.biology.cufes_fetch import BBox, build_erddap_csv_url, fetch_cufes
from fishai.ingestion.biology.cufes_pipeline import sync_cufes
from fishai.ingestion.biology.cufes_transform import (
    make_event_id,
    make_sample_id,
    qc_flags_for_row,
    transform_rows,
    volume_m3_for_row,
)

SOURCE_MODULE = "calcofi_cufes"

__all__ = [
    "SOURCE_ID",
    "SOURCE_MODULE",
    "BBox",
    "build_erddap_csv_url",
    "fetch_cufes",
    "sync_cufes",
    "make_event_id",
    "make_sample_id",
    "qc_flags_for_row",
    "transform_rows",
    "volume_m3_for_row",
]
