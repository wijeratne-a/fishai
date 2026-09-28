"""GLORYS must refuse require_approved in pilot manifest."""

from __future__ import annotations

import datetime as dt

import pytest

from fishai.ingestion.physics.sources.glorys import PRODUCT_ID, PRODUCT_TIME_END, PRODUCT_TIME_START, VARIABLES
from fishai.ingestion.sources import SourceNotApprovedError, require_approved


def test_glorys_product_variables_use_bottom_t() -> None:
    assert PRODUCT_ID == "cmems_mod_glo_phy_my_0.083deg_P1D-m"
    assert "bottomT" in VARIABLES
    assert "tob" not in VARIABLES
    assert PRODUCT_TIME_START == dt.date(1993, 1, 1)
    assert PRODUCT_TIME_END == dt.date(2026, 6, 23)


def test_glorys_require_approved_blocked() -> None:
    with pytest.raises(SourceNotApprovedError):
        require_approved("glorys")


def test_glorys_fetch_blocked() -> None:
    from fishai.ingestion.physics.sources.glorys import fetch_day

    with pytest.raises(SourceNotApprovedError):
        fetch_day(dt.date(2020, 1, 1), (32.0, 35.0, -121.0, -117.0))
