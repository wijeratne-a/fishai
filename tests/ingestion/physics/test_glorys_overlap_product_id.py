"""Overlap window must resolve GLORYS ids from catalog coverage."""

from fishai.ingestion.physics.sources.glorys import PRODUCT_ID_MY, glorys_dataset_id_for_date
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, overlap_dates


def test_every_overlap_day_resolves_to_my_product() -> None:
    cfg = load_overlap_config()
    for day in overlap_dates(cfg):
        assert glorys_dataset_id_for_date(day, config=cfg) == PRODUCT_ID_MY
