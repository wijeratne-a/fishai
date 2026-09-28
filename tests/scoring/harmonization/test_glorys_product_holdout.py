"""Holdout window uses glorys_product_for_date from bot2 (#7)."""

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


def test_my_myint_boundary_dates() -> None:
    cfg = load_overlap_config()
    assert glorys_product_for_date(dt.date(2021, 6, 30), config=cfg) == PRODUCT_ID_MY
    assert glorys_product_for_date(dt.date(2021, 7, 1), config=cfg) == PRODUCT_ID_MYINT
