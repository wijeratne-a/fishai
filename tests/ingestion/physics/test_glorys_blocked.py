"""Legacy module name kept; compliance tests live in test_glorys_compliance.py."""

from __future__ import annotations

import datetime as dt

import pytest

from fishai.ingestion.physics.sources.glorys import PRODUCT_TIME_END, PRODUCT_TIME_START, VARIABLES
from fishai.ingestion.sources import SourceNotApprovedError, require_approved


def test_glorys_product_metadata() -> None:
    assert "bottomT" in VARIABLES
    assert "tob" not in VARIABLES
    assert PRODUCT_TIME_START == dt.date(1993, 1, 1)
    assert PRODUCT_TIME_END == dt.date(2026, 6, 23)


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
