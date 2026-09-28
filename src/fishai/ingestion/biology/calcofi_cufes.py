"""CalCOFI CUFES egg counts via ERDDAP ``erdCalCOFIcufes``.

Pump speed units (ERDDAP ``erdCalCOFIcufes.das``): ``M^3 per minute`` — effort volume is
mean of available positive pump speeds × sample duration in minutes, yielding m³.
``pump_readings_used`` on ``cufes_events`` is 1 or 2; when only one of start/stop pump
speed is valid, volume uses that single reading (no synthetic fill for the missing value).

Processed ``cufes_events.parquet`` uses ``event_id`` as the join key to physics and
modeling code. Effort offset for delta models uses ``log(volume_m3)`` with **no**
additive offset unless a model config states otherwise.

License on ERDDAP (not CC-BY): NOAA free-use disclaimer; see ``data/SOURCES.yaml``.
"""

from __future__ import annotations

from fishai.ingestion.biology.cufes import (
    SOURCE_ID,
    BBox,
    TransformResult,
    build_erddap_csv_url,
    fetch_cufes,
    make_event_id,
    qc_flags_for_row,
    sync_cufes,
    transform_rows,
    volume_m3_for_row,
)

SOURCE_MODULE = "calcofi_cufes"

__all__ = [
    "SOURCE_ID",
    "SOURCE_MODULE",
    "BBox",
    "TransformResult",
    "build_erddap_csv_url",
    "fetch_cufes",
    "sync_cufes",
    "make_event_id",
    "qc_flags_for_row",
    "transform_rows",
    "volume_m3_for_row",
]
