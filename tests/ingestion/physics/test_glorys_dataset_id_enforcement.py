"""GLORYS dataset_id must match glorys_product_for_date (no silent override)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from fishai.ingestion.physics.sources.glorys import (
    PRODUCT_ID_MY,
    fetch_day,
    glorys_dataset_id_for_date,
    glorys_product_for_date,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
GLORYS_SRC = REPO_ROOT / "src" / "fishai" / "ingestion" / "physics"
DEPRECATED_MYINT_PRODUCT_ID = "cmems_mod_glo_phy_myint_0.083deg_P1D-m"


def test_mismatched_dataset_id_raises() -> None:
    with pytest.raises(ValueError, match="does not match"):
        glorys_dataset_id_for_date(dt.date(2024, 9, 1), DEPRECATED_MYINT_PRODUCT_ID)
    with pytest.raises(ValueError, match="does not match"):
        glorys_dataset_id_for_date(dt.date(2021, 6, 30), DEPRECATED_MYINT_PRODUCT_ID)


def test_matching_dataset_id_accepted() -> None:
    day = dt.date(2024, 9, 1)
    assert glorys_dataset_id_for_date(day, PRODUCT_ID_MY) == PRODUCT_ID_MY
    day_my = dt.date(2021, 6, 30)
    assert glorys_dataset_id_for_date(day_my, PRODUCT_ID_MY) == PRODUCT_ID_MY


def test_none_uses_date_rule() -> None:
    day = dt.date(1998, 1, 1)
    assert glorys_dataset_id_for_date(day, None) == glorys_product_for_date(day)


def test_fetch_day_rejects_wrong_dataset_id(tmp_path: Path) -> None:
    bbox = (32.0, 35.0, -121.0, -117.0)

    def fake_fetch() -> dict:
        return {"variables": ["thetao"]}

    with pytest.raises(ValueError, match="does not match"):
        fetch_day(
            dt.date(2024, 9, 1),
            bbox,
            purpose="hindcast",
            fetch_fn=fake_fetch,
            log_path=tmp_path / "log.jsonl",
            dataset_id=DEPRECATED_MYINT_PRODUCT_ID,
        )


def test_fetch_day_accepts_correct_dataset_id(tmp_path: Path) -> None:
    bbox = (32.0, 35.0, -121.0, -117.0)
    day = dt.date(2024, 9, 1)

    def fake_fetch() -> dict:
        return {"variables": ["thetao"]}

    fetch_day(
        day,
        bbox,
        purpose="hindcast",
        fetch_fn=fake_fetch,
        log_path=tmp_path / "log.jsonl",
        dataset_id=PRODUCT_ID_MY,
    )


def test_no_dataset_id_or_fallback_in_glorys_physics_src() -> None:
    """Call sites must not bypass date-based product selection."""
    offenders: list[str] = []
    for path in GLORYS_SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "dataset_id or" in text:
            offenders.append(f"{path.relative_to(REPO_ROOT)}: dataset_id or")
        if "product_id or" in text and "glorys" in path.name:
            offenders.append(f"{path.relative_to(REPO_ROOT)}: product_id or")
    assert not offenders, "forbidden GLORYS id fallback: " + "; ".join(offenders)
