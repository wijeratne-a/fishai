"""NDBC meteorological/ocean stations (``cwwcNDBCMet`` ERDDAP)."""

from fishai.ingestion.sources import require_approved

SOURCE_MODULE = "ndbc_met"
SOURCE_ID = "ndbc_met"


def ensure_approved() -> dict:
    return require_approved(SOURCE_ID)
