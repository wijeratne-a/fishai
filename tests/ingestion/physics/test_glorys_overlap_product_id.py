"""Overlap window must resolve to the interim GLORYS product."""

from __future__ import annotations

import datetime as dt

from fishai.ingestion.physics.sources.glorys import PRODUCT_ID_MYINT, resolve_glorys_product_id
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, overlap_dates


def test_every_overlap_day_resolves_to_myint_product() -> None:
    cfg = load_overlap_config()
    expected = cfg["glorys"]["product_id"]
    assert expected == PRODUCT_ID_MYINT
    for day in overlap_dates(cfg):
        assert resolve_glorys_product_id(day, cfg) == PRODUCT_ID_MYINT
    assert resolve_glorys_product_id(dt.date(2025, 1, 1), cfg) == PRODUCT_ID_MYINT
