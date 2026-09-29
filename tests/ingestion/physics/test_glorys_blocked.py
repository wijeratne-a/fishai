"""Legacy module name kept; compliance tests live in test_glorys_compliance.py."""

from __future__ import annotations

import datetime as dt

import pytest

from fishai.ingestion.physics.sources.glorys import (
    MY_COVERAGE_END_DEFAULT,
    MY_PRODUCT_START,
    PRODUCT_ID_MY,
    VARIABLES,
    glorys_product_for_date,
)
from fishai.ingestion.sources import require_approved


def test_glorys_product_metadata() -> None:
    assert "bottomT" in VARIABLES
    assert "tob" not in VARIABLES
    assert MY_PRODUCT_START == dt.date(1993, 1, 1)
    assert MY_COVERAGE_END_DEFAULT == dt.date(2026, 6, 23)
    assert glorys_product_for_date(dt.date(2021, 6, 30)) == PRODUCT_ID_MY
    assert glorys_product_for_date(dt.date(2021, 7, 1)) == PRODUCT_ID_MY


def test_glorys_without_purpose_is_approved() -> None:
    require_approved("glorys")


def test_fetch_without_client_raises(tmp_path) -> None:
    from fishai.ingestion.physics.sources.glorys import fetch_day

    with pytest.raises(RuntimeError, match="fetch_fn"):
        fetch_day(
            dt.date(2020, 1, 1),
            (32.0, 35.0, -121.0, -117.0),
            purpose="training",
            log_path=tmp_path / "log.jsonl",
        )
