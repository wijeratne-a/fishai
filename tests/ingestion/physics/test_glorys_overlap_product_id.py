"""Overlap window must resolve to the interim GLORYS product (date-based)."""

from fishai.ingestion.physics.sources.glorys import PRODUCT_ID_MYINT, glorys_product_for_date
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, overlap_dates


def test_every_overlap_day_resolves_to_myint_product() -> None:
    cfg = load_overlap_config()
    for day in overlap_dates(cfg):
        assert glorys_product_for_date(day, config=cfg) == PRODUCT_ID_MYINT
