"""Holdout window must use date-based GLORYS product selection from bot2 (#7)."""

from __future__ import annotations

import datetime as dt

from fishai.ingestion.physics.sources.glorys import (
    PRODUCT_ID_MY,
    PRODUCT_ID_MYINT,
    glorys_product_for_date,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config


def test_holdout_window_uses_myint_product() -> None:
    cfg = load_overlap_config()
    assert glorys_product_for_date(dt.date(2025, 9, 1), config=cfg) == PRODUCT_ID_MYINT
    assert glorys_product_for_date(dt.date(2026, 6, 23), config=cfg) == PRODUCT_ID_MYINT


def test_date_before_myint_uses_my_product() -> None:
    cfg = load_overlap_config()
    assert glorys_product_for_date(dt.date(2021, 6, 30), config=cfg) == PRODUCT_ID_MY
    assert glorys_product_for_date(dt.date(1998, 3, 1), config=cfg) == PRODUCT_ID_MY
