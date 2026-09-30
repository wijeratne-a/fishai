"""CUFES covariate source_product must match glorys_product_for_date (PR #7)."""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

import pytest

from fishai.ingestion.physics.sources.glorys import glorys_product_for_date
from fishai.models.cufes_source_product import (
    assert_source_products_match_glorys,
    find_source_product_mismatches,
    parse_event_utc_date,
)

REPO = Path(__file__).resolve().parents[2]
EVENTS = REPO / "src" / "models" / "tests" / "fixtures" / "synthetic_cufes_events.csv"
COV = REPO / "src" / "models" / "tests" / "fixtures" / "synthetic_cufes_covariates.csv"


def test_fixture_covariates_match_glorys_product_for_date() -> None:
    events = list(csv.DictReader(EVENTS.open(encoding="utf-8")))
    cov = {row["event_id"]: row for row in csv.DictReader(COV.open(encoding="utf-8"))}
    assert "source_product" in next(iter(cov.values()), {}), "fixture missing source_product column"
    mismatches = find_source_product_mismatches(
        [e["event_id"] for e in events],
        [e["time"] for e in events],
        [cov[e["event_id"]]["source_product"] for e in events],
    )
    assert mismatches == []


def test_mismatch_detection_fails() -> None:
    day = dt.date(2021, 7, 1)
    expected = glorys_product_for_date(day)
    wrong = "cmems_mod_glo_phy_my_0.083deg_P1D-m" if expected != "cmems_mod_glo_phy_my_0.083deg_P1D-m" else "bad-product"
    with pytest.raises(ValueError, match="glorys_product_for_date"):
        assert_source_products_match_glorys(
            ["e1"],
            ["2021-07-01T12:00:00Z"],
            [wrong],
        )


def test_parse_event_utc_date_accepts_z_suffix() -> None:
    assert parse_event_utc_date("2020-06-01T12:00:00Z") == dt.date(2020, 6, 1)


def test_data_provenance_tree_not_modified_during_tests(repo_provenance_snapshot) -> None:
    root = REPO / "data" / "provenance"
    snap = {
        str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }
    assert snap == repo_provenance_snapshot
