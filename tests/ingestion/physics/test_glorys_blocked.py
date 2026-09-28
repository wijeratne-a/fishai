"""GLORYS must refuse require_approved in pilot manifest."""

from __future__ import annotations

import datetime as dt

import pytest

from fishai.ingestion.sources import SourceNotApprovedError, require_approved


def test_glorys_require_approved_blocked() -> None:
    with pytest.raises(SourceNotApprovedError):
        require_approved("glorys")


def test_glorys_fetch_blocked() -> None:
    from fishai.ingestion.physics.sources.glorys import fetch_day

    with pytest.raises(SourceNotApprovedError):
        fetch_day(dt.date(2020, 1, 1), (32.0, 35.0, -121.0, -117.0))
