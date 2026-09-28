"""Recorded WCOFS avg.nowcast gaps in the fit window (PR #14 item 7)."""

from __future__ import annotations

import datetime as dt

import pytest

from fishai.ingestion.physics.wcofs_avg_nowcast_availability import (
    assert_wcofs_avg_nowcast_available,
    wcofs_avg_nowcast_missing_fit_days,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import build_overlap_metadata, load_overlap_config
from fishai.physics.store import CycleNotAvailable


def test_recorded_fit_gap_count_and_dates() -> None:
    cfg = load_overlap_config()
    missing = wcofs_avg_nowcast_missing_fit_days(cfg)
    assert len(missing) == 44
    assert dt.date(2024, 9, 5) in missing
    assert dt.date(2024, 9, 6) in missing
    assert dt.date(2024, 11, 20) in missing
    assert dt.date(2024, 12, 31) in missing
    assert dt.date(2024, 11, 19) not in missing
    assert dt.date(2025, 1, 1) not in missing


def test_assert_wcofs_avg_nowcast_available_raises_cycle_not_available() -> None:
    cfg = load_overlap_config()
    with pytest.raises(CycleNotAvailable, match="avg.nowcast"):
        assert_wcofs_avg_nowcast_available(dt.date(2024, 9, 5), cfg)


def test_overlap_metadata_lists_missing_fit_days_with_reason() -> None:
    cfg = load_overlap_config()
    meta = build_overlap_metadata(cfg)
    records = meta["wcofs_avg_nowcast_missing_fit_days"]
    assert len(records) == 44
    assert all(r["reason_code"] == "CycleNotAvailable" for r in records)
    assert records[0]["product"] == "avg.nowcast"
