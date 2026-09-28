"""Date-based GLORYS product selection via live catalogue coverage."""

from __future__ import annotations

import datetime as dt

import pytest

from fishai.ingestion.physics.glorys_catalog import GlorysCatalogError
from fishai.ingestion.physics.sources.glorys import (
    MY_PRODUCT_START,
    PRODUCT_ID_MY,
    glorys_product_for_date,
    resolve_glorys_product_id,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, overlap_dates


def test_my_on_last_reanalysis_day() -> None:
    assert glorys_product_for_date(dt.date(2021, 6, 30)) == PRODUCT_ID_MY


def test_my_in_hindcast_window() -> None:
    assert glorys_product_for_date(dt.date(1998, 3, 15)) == PRODUCT_ID_MY


def test_my_serves_overlap_era() -> None:
    assert glorys_product_for_date(dt.date(2025, 9, 1)) == PRODUCT_ID_MY


def test_before_my_start_raises() -> None:
    with pytest.raises(ValueError, match="before"):
        glorys_product_for_date(dt.date(1992, 12, 31))


def test_after_catalog_end_raises() -> None:
    with pytest.raises(GlorysCatalogError) as exc:
        glorys_product_for_date(dt.date(2030, 1, 1))
    assert exc.value.reason_code == "glorys_date_not_covered"


def test_overlap_window_uses_catalog_my() -> None:
    cfg = load_overlap_config()
    for day in overlap_dates(cfg):
        assert resolve_glorys_product_id(day, cfg) == PRODUCT_ID_MY
    assert MY_PRODUCT_START <= overlap_dates(cfg)[0]
