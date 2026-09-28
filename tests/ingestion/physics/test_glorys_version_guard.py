"""GLORYS catalogue version guard on reruns."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest

from fishai.ingestion.copernicus_compliance import append_pull_log, build_pull_record
from fishai.ingestion.physics.glorys_catalog import (
    GlorysCatalogEntry,
    GlorysCatalogError,
    clear_glorys_catalog_cache,
    set_catalog_fetch_hook,
)
from fishai.ingestion.physics.sources.glorys import PRODUCT_ID_MY, fetch_day


def test_fetch_day_blocks_catalog_version_change(tmp_path: Path) -> None:
    log_path = tmp_path / "copernicus_pull_log.jsonl"
    bbox = (32.0, 35.0, -121.0, -117.0)
    append_pull_log(
        build_pull_record(
            dataset_id=PRODUCT_ID_MY,
            date_start="2020-06-01",
            date_end="2020-06-01",
            variables=("thetao",),
            bbox=bbox,
        )
        | {
            "dataset_version": "202311",
            "catalog_coverage": {"start": "1993-01-01", "end": "2026-06-23"},
        },
        log_path=log_path,
    )
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(
        lambda: [
            GlorysCatalogEntry(
                dataset_id=PRODUCT_ID_MY,
                dataset_version="202406",
                coverage_start=dt.date(1993, 1, 1),
                coverage_end=dt.date(2026, 6, 23),
            )
        ]
    )

    def fake_fetch() -> dict:
        raise AssertionError("fetch_fn must not run when version guard blocks the pull")

    with pytest.raises(GlorysCatalogError) as exc:
        fetch_day(
            dt.date(2020, 6, 1),
            bbox,
            purpose="hindcast",
            fetch_fn=fake_fetch,
            log_path=log_path,
        )
    assert exc.value.reason_code == "glorys_dataset_version_changed"

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    failure = json.loads(lines[1])
    assert failure["reason_code"] == "glorys_dataset_version_changed"
    assert failure["recorded_dataset_version"] == "202311"
    assert failure["dataset_version"] == "202406"
    assert "date_start" not in failure
