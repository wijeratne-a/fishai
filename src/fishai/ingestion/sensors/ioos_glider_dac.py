"""IOOS Glider DAC tracks for holdout checks against physics.

License pending in ``data/SOURCES.yaml``; ingestion remains disabled until review completes.
"""

from fishai.ingestion.sources import require_approved

SOURCE_MODULE = "ioos_glider_dac"
SOURCE_ID = "ioos_glider_dac"


def ensure_approved() -> dict:
    return require_approved(SOURCE_ID)
