"""Overlap window must resolve to the interim GLORYS product (date-based)."""

from fishai.ingestion.physics.sources.glorys import PRODUCT_ID_MYINT, resolve_glorys_product_id
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, overlap_dates


def test_every_overlap_day_resolves_to_myint_product() -> None:
    cfg = load_overlap_config()
    for day in overlap_dates(cfg):
        assert resolve_glorys_product_id(day, cfg) == PRODUCT_ID_MYINT
