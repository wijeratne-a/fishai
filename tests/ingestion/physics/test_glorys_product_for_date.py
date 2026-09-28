"""Date-based GLORYS product selection from catalog coverage."""

from __future__ import annotations

import datetime as dt

import pytest

from fishai.ingestion.physics.sources.glorys import (
    PRODUCT_ID_MY,
    glorys_product_for_date,
    resolve_glorys_product_id,
)
from fishai.ingestion.physics.sources.glorys_catalog import GlorysDatasetNotCoveredError
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, overlap_dates


def test_overlap_era_uses_my_per_live_catalog_record() -> None:
    cfg = load_overlap_config()
    assert glorys_product_for_date(dt.date(2021, 6, 30), config=cfg) == PRODUCT_ID_MY
    assert glorys_product_for_date(dt.date(2021, 7, 1), config=cfg) == PRODUCT_ID_MY
    assert glorys_product_for_date(dt.date(2025, 9, 1), config=cfg) == PRODUCT_ID_MY


def test_before_catalog_start_raises() -> None:
    cfg = load_overlap_config()
    with pytest.raises(GlorysDatasetNotCoveredError):
        glorys_product_for_date(dt.date(1992, 12, 31), config=cfg)


def test_after_catalog_end_raises() -> None:
    cfg = load_overlap_config()
    with pytest.raises(GlorysDatasetNotCoveredError):
        glorys_product_for_date(dt.date(2027, 1, 1), config=cfg)


def test_overlap_window_uses_my() -> None:
    cfg = load_overlap_config()
    for day in overlap_dates(cfg):
        assert resolve_glorys_product_id(day, cfg) == PRODUCT_ID_MY
