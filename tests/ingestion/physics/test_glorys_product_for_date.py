"""Date-based GLORYS MY vs MYINT product selection."""

from __future__ import annotations

import datetime as dt

import pytest

from fishai.ingestion.physics.sources.glorys import (
    MY_PRODUCT_END,
    MYINT_PRODUCT_START,
    PRODUCT_ID_MY,
    PRODUCT_ID_MYINT,
    glorys_product_for_date,
    resolve_glorys_product_id,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, overlap_dates


def test_my_on_last_reanalysis_day() -> None:
    assert glorys_product_for_date(dt.date(2021, 6, 30)) == PRODUCT_ID_MY


def test_myint_from_interim_start() -> None:
    assert glorys_product_for_date(dt.date(2021, 7, 1)) == PRODUCT_ID_MYINT


def test_my_in_hindcast_window() -> None:
    assert glorys_product_for_date(dt.date(1998, 3, 15)) == PRODUCT_ID_MY


def test_myint_in_overlap_era() -> None:
    assert glorys_product_for_date(dt.date(2025, 9, 1)) == PRODUCT_ID_MYINT


def test_before_my_start_raises() -> None:
    with pytest.raises(ValueError, match="before"):
        glorys_product_for_date(dt.date(1992, 12, 31))


def test_after_myint_end_raises() -> None:
    cfg = load_overlap_config()
    with pytest.raises(ValueError, match="after myint"):
        glorys_product_for_date(dt.date(2027, 1, 1), config=cfg)


def test_overlap_window_uses_myint() -> None:
    cfg = load_overlap_config()
    for day in overlap_dates(cfg):
        assert resolve_glorys_product_id(day, cfg) == PRODUCT_ID_MYINT
    assert MY_PRODUCT_END < overlap_dates(cfg)[0]
    assert overlap_dates(cfg)[0] >= MYINT_PRODUCT_START
