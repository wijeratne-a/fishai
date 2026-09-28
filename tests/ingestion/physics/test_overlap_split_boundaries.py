"""Train/test split labels from overlap config."""

from __future__ import annotations

import datetime as dt

from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, overlap_dates, split_label


def test_split_dates_in_config_match_literals() -> None:
    cfg = load_overlap_config()
    assert str(cfg["split"]["fit_end"]) == "2025-08-31"
    assert str(cfg["split"]["test_start"]) == "2025-09-01"


def test_split_labels_at_boundaries() -> None:
    cfg = load_overlap_config()
    fit_end = dt.date.fromisoformat(str(cfg["split"]["fit_end"]))
    test_start = dt.date.fromisoformat(str(cfg["split"]["test_start"]))
    assert fit_end == dt.date(2025, 8, 31)
    assert test_start == dt.date(2025, 9, 1)
    assert split_label(fit_end, cfg) == "fit"
    assert split_label(test_start, cfg) == "test"
    assert split_label(dt.date(2024, 9, 1), cfg) == "fit"
    assert split_label(dt.date(2026, 6, 23), cfg) == "test"


def test_overlap_dates_span_only_configured_window() -> None:
    cfg = load_overlap_config()
    days = overlap_dates(cfg)
    start = dt.date.fromisoformat(str(cfg["overlap"]["start"]))
    end = dt.date.fromisoformat(str(cfg["overlap"]["end"]))
    assert days[0] == start
    assert days[-1] == end
    assert len(days) == int(cfg["overlap"]["expected_days"])
