"""PR #14: overlap defers GLORYS ids to shared ``glorys_dataset_id_for_date``."""

from __future__ import annotations

import datetime as dt

import pytest

from fishai.ingestion.physics.sources.glorys import PRODUCT_ID_MYINT, glorys_dataset_id_for_date
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    REASON_GLORYS_DATASET_RESOLUTION,
    OverlapGlorysDayMissingError,
    glorys_dataset_id_for_overlap_day,
    load_overlap_config,
)


def test_overlap_day_delegates_to_shared_glorys_dataset_id_for_date() -> None:
    cfg = load_overlap_config()
    day = dt.date(2024, 9, 1)
    assert glorys_dataset_id_for_overlap_day(day, cfg) == glorys_dataset_id_for_date(day, config=cfg)
    assert glorys_dataset_id_for_overlap_day(day, cfg) == PRODUCT_ID_MYINT


def test_shared_glorys_errors_become_overlap_missing_day_with_reason() -> None:
    cfg = load_overlap_config()
    with pytest.raises(OverlapGlorysDayMissingError) as excinfo:
        glorys_dataset_id_for_overlap_day(dt.date(1992, 12, 31), cfg)
    assert excinfo.value.reason_code == REASON_GLORYS_DATASET_RESOLUTION
