"""SCCOOS HF radar (UCSD W6) surface currents for consistency checks."""

from fishai.ingestion.sources import require_approved

SOURCE_MODULE = "sccoos_hfr"
SOURCE_ID = "sccoos_hfr"


def ensure_approved() -> dict:
    return require_approved(SOURCE_ID)
