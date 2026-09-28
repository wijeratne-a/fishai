"""GLORYS dataset id selection from Copernicus Marine catalog coverage (PR #14 item 7)."""

from __future__ import annotations

import datetime as dt
from types import SimpleNamespace

import pytest

from fishai.ingestion.physics.sources.glorys import (
    PRODUCT_ID_MY,
    PRODUCT_ID_MYINT,
    glorys_product_for_date,
)
from fishai.ingestion.physics.sources.glorys_catalog import (
    REASON_GLORYS_DATE_NOT_COVERED,
    GlorysDatasetNotCoveredError,
    describe_dataset_record,
    glorys_dataset_id_for_calendar_day,
    refresh_catalog_into_config,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config


def _catalogue_with_time(start_ms: float, end_ms: float, version: str = "202311"):
    time_coord = SimpleNamespace(
        coordinate_id="time",
        minimum_value=start_ms,
        maximum_value=end_ms,
    )
    variable = SimpleNamespace(coordinates=[time_coord], short_name="thetao")
    service = SimpleNamespace(variables=[variable])
    part = SimpleNamespace(services=[service])
    version_obj = SimpleNamespace(label=version, parts=[part])
    dataset = SimpleNamespace(versions=[version_obj])
    product = SimpleNamespace(datasets=[dataset])
    return SimpleNamespace(products=[product])


def test_overlap_era_uses_my_when_myint_missing_from_catalog() -> None:
    cfg = load_overlap_config()
    assert glorys_product_for_date(dt.date(2024, 9, 1), config=cfg) == PRODUCT_ID_MY
    assert glorys_product_for_date(dt.date(2026, 6, 23), config=cfg) == PRODUCT_ID_MY


def test_uncovered_date_fails_with_reason_code() -> None:
    cfg = load_overlap_config()
    with pytest.raises(GlorysDatasetNotCoveredError) as excinfo:
        glorys_dataset_id_for_calendar_day(dt.date(1992, 12, 31), cfg)
    assert excinfo.value.reason_code == REASON_GLORYS_DATE_NOT_COVERED


def test_describe_dataset_not_found_marks_product_unavailable() -> None:
    def _missing(_dataset_id: str):
        raise RuntimeError("Dataset not found: cmems_mod_glo_phy_myint_0.083deg_P1D-m")

    rec = describe_dataset_record("myint", PRODUCT_ID_MYINT, describe_fn=_missing)
    assert rec.catalog_status == "dataset_not_found"
    assert rec.temporal_start is None


def test_refresh_catalog_records_my_coverage_from_describe() -> None:
    start = 725846400000.0  # 1993-01-01
    end = 1782172800000.0  # 2026-06-23

    def _describe(dataset_id: str):
        if dataset_id == PRODUCT_ID_MYINT:
            raise RuntimeError("Dataset not found")
        return _catalogue_with_time(start, end)

    cfg = load_overlap_config()
    refreshed = refresh_catalog_into_config(
        cfg,
        describe_fn=_describe,
        copernicusmarine_version="2.5.0",
        checked_at=dt.date(2026, 9, 28),
    )
    my = refreshed["glorys"]["catalog"]["products"]["my"]
    assert my["catalog_status"] == "found"
    assert my["temporal_end"] == "2026-06-23"
    assert glorys_product_for_date(dt.date(2024, 9, 1), config=refreshed) == PRODUCT_ID_MY
