"""GLORYS catalogue version guard on reruns and first-run pinned version."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from fishai.ingestion.copernicus_compliance import append_pull_log, build_pull_record
from unittest.mock import patch

from fishai.ingestion.physics.glorys_catalog import (
    GlorysCatalogEntry,
    GlorysCatalogError,
    GlorysDatasetResolution,
    clear_glorys_catalog_cache,
    pinned_glorys_catalog_version,
    set_catalog_fetch_hook,
    write_glorys_pull_log_record,
)
from fishai.ingestion.physics.sources.glorys import PRODUCT_ID_MY, fetch_day
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, run_overlap_pairing


def _my_entry(version: str) -> list[GlorysCatalogEntry]:
    return [
        GlorysCatalogEntry(
            dataset_id=PRODUCT_ID_MY,
            dataset_version=version,
            coverage_start=dt.date(1993, 1, 1),
            coverage_end=dt.date(2026, 6, 23),
        )
    ]


def test_write_pull_log_record_does_not_invoke_version_guard(tmp_path: Path) -> None:
    resolution = GlorysDatasetResolution(
        dataset_id=PRODUCT_ID_MY,
        dataset_version="202311",
        catalog_coverage={"start": "1993-01-01", "end": "2026-06-23"},
    )
    log_path = tmp_path / "log.jsonl"
    bbox = (32.0, 35.0, -121.0, -117.0)
    with patch(
        "fishai.ingestion.physics.glorys_catalog.ensure_glorys_dataset_version_allowed"
    ) as guard:
        write_glorys_pull_log_record(
            dt.date(2020, 6, 1),
            resolution,
            variables=("thetao",),
            bbox=bbox,
            log_path=log_path,
        )
        guard.assert_not_called()


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
    set_catalog_fetch_hook(lambda: _my_entry("202406"))

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


def test_fetch_day_empty_log_requires_pinned_catalog_version(tmp_path: Path) -> None:
    log_path = tmp_path / "copernicus_pull_log.jsonl"
    bbox = (32.0, 35.0, -121.0, -117.0)
    pinned = pinned_glorys_catalog_version()
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(lambda: _my_entry(pinned))

    fetch_day(
        dt.date(2020, 6, 1),
        bbox,
        purpose="hindcast",
        fetch_fn=lambda: {"variables": ["thetao"]},
        log_path=log_path,
    )
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["dataset_version"] == pinned


def test_fetch_day_empty_log_rejects_unpinned_catalog_version(tmp_path: Path) -> None:
    log_path = tmp_path / "copernicus_pull_log.jsonl"
    bbox = (32.0, 35.0, -121.0, -117.0)
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(lambda: _my_entry("202406"))

    def fake_fetch() -> dict:
        raise AssertionError("fetch_fn must not run when pinned version guard blocks the pull")

    with pytest.raises(GlorysCatalogError) as exc:
        fetch_day(
            dt.date(2020, 6, 1),
            bbox,
            purpose="hindcast",
            fetch_fn=fake_fetch,
            log_path=log_path,
        )
    assert exc.value.reason_code == "glorys_dataset_version_not_pinned"
    failure = json.loads(log_path.read_text(encoding="utf-8").strip().splitlines()[0])
    assert failure["reason_code"] == "glorys_dataset_version_not_pinned"
    assert "date_start" not in failure


def test_fetch_day_writes_pull_log_only_after_successful_fetch(tmp_path: Path) -> None:
    log_path = tmp_path / "copernicus_pull_log.jsonl"
    bbox = (32.0, 35.0, -121.0, -117.0)
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(lambda: _my_entry(pinned_glorys_catalog_version()))

    def failing_fetch() -> dict:
        raise RuntimeError("simulated Copernicus failure")

    with pytest.raises(RuntimeError, match="simulated"):
        fetch_day(
            dt.date(2020, 6, 1),
            bbox,
            purpose="hindcast",
            fetch_fn=failing_fetch,
            log_path=log_path,
        )
    assert not log_path.exists()


def test_overlap_blocks_version_change_without_fetch(tmp_path: Path) -> None:
    cfg = load_overlap_config()
    cfg = dict(cfg)
    cfg["pilot_bbox"] = {
        "lat_min": 33.0,
        "lat_max": 33.3,
        "lon_min": -120.5,
        "lon_max": -120.2,
    }
    cfg["pull_logs"] = {
        "wcofs": str(tmp_path / "wcofs_pull_log.jsonl"),
        "glorys": str(tmp_path / "copernicus_pull_log.jsonl"),
    }
    glorys_log = tmp_path / "copernicus_pull_log.jsonl"
    bbox = (
        float(cfg["pilot_bbox"]["lat_min"]),
        float(cfg["pilot_bbox"]["lat_max"]),
        float(cfg["pilot_bbox"]["lon_min"]),
        float(cfg["pilot_bbox"]["lon_max"]),
    )
    append_pull_log(
        build_pull_record(
            dataset_id=PRODUCT_ID_MY,
            date_start="2024-09-01",
            date_end="2024-09-01",
            variables=("thetao", "so"),
            bbox=bbox,
        )
        | {
            "dataset_version": "202311",
            "catalog_coverage": {"start": "1993-01-01", "end": "2026-06-23"},
        },
        log_path=glorys_log,
    )
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(lambda: _my_entry("202406"))
    fetch_calls = 0

    def wcofs_open(_day: dt.date) -> xr.Dataset:
        n = 4
        return xr.Dataset(
            {
                "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), np.ones((1, 2, n, n))),
                "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), np.full((1, 2, n, n), 33.5)),
                "zeta": (("eta_rho", "xi_rho"), np.zeros((n, n))),
                "h": (("eta_rho", "xi_rho"), np.full((n, n), 100.0)),
                "mask_rho": (("eta_rho", "xi_rho"), np.ones((n, n))),
                "lat_rho": (("eta_rho", "xi_rho"), np.linspace(33.0, 33.3, n)[:, None] * np.ones((n, n))),
                "lon_rho": (("eta_rho", "xi_rho"), np.linspace(-120.5, -120.2, n)[None, :] * np.ones((n, n))),
                "pm": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
                "pn": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
                "hc": 50.0,
                "s_rho": ("s_rho", np.array([-0.75, -0.25])),
                "Cs_r": ("s_rho", np.array([-0.5, 0.0])),
            }
        )

    def glorys_fetch(_day: dt.date) -> dict:
        nonlocal fetch_calls
        fetch_calls += 1
        raise AssertionError("glorys_fetch must not run when version guard blocks overlap pull")

    with pytest.raises(GlorysCatalogError) as exc:
        run_overlap_pairing(
            config=cfg,
            days=[dt.date(2024, 9, 1)],
            wcofs_open=wcofs_open,
            glorys_fetch=glorys_fetch,
        )
    assert exc.value.reason_code == "glorys_dataset_version_changed"
    assert fetch_calls == 0


def test_overlap_empty_log_rejects_unpinned_catalog_version(tmp_path: Path) -> None:
    cfg = load_overlap_config()
    cfg = dict(cfg)
    cfg["pilot_bbox"] = {
        "lat_min": 33.0,
        "lat_max": 33.3,
        "lon_min": -120.5,
        "lon_max": -120.2,
    }
    cfg["pull_logs"] = {
        "wcofs": str(tmp_path / "wcofs_pull_log.jsonl"),
        "glorys": str(tmp_path / "copernicus_pull_log.jsonl"),
    }
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(lambda: _my_entry("202406"))
    fetch_calls = 0

    def wcofs_open(_day: dt.date) -> xr.Dataset:
        n = 4
        return xr.Dataset(
            {
                "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), np.ones((1, 2, n, n))),
                "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), np.full((1, 2, n, n), 33.5)),
                "zeta": (("eta_rho", "xi_rho"), np.zeros((n, n))),
                "h": (("eta_rho", "xi_rho"), np.full((n, n), 100.0)),
                "mask_rho": (("eta_rho", "xi_rho"), np.ones((n, n))),
                "lat_rho": (("eta_rho", "xi_rho"), np.linspace(33.0, 33.3, n)[:, None] * np.ones((n, n))),
                "lon_rho": (("eta_rho", "xi_rho"), np.linspace(-120.5, -120.2, n)[None, :] * np.ones((n, n))),
                "pm": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
                "pn": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
                "hc": 50.0,
                "s_rho": ("s_rho", np.array([-0.75, -0.25])),
                "Cs_r": ("s_rho", np.array([-0.5, 0.0])),
            }
        )

    def glorys_fetch(_day: dt.date) -> dict:
        nonlocal fetch_calls
        fetch_calls += 1
        raise AssertionError("glorys_fetch must not run when pinned version guard blocks overlap pull")

    with pytest.raises(GlorysCatalogError) as exc:
        run_overlap_pairing(
            config=cfg,
            days=[dt.date(2024, 9, 1)],
            wcofs_open=wcofs_open,
            glorys_fetch=glorys_fetch,
        )
    assert exc.value.reason_code == "glorys_dataset_version_not_pinned"
    assert fetch_calls == 0


def test_overlap_writes_pull_log_only_after_successful_fetch(tmp_path: Path) -> None:
    cfg = load_overlap_config()
    cfg = dict(cfg)
    cfg["pilot_bbox"] = {
        "lat_min": 33.0,
        "lat_max": 33.3,
        "lon_min": -120.5,
        "lon_max": -120.2,
    }
    cfg["pull_logs"] = {
        "wcofs": str(tmp_path / "wcofs_pull_log.jsonl"),
        "glorys": str(tmp_path / "copernicus_pull_log.jsonl"),
    }
    glorys_log = tmp_path / "copernicus_pull_log.jsonl"
    z_levels = np.array([0.0, 1.0, 3.0, 10.0])
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(lambda: _my_entry(pinned_glorys_catalog_version()))

    def wcofs_open(_day: dt.date) -> xr.Dataset:
        n = 4
        return xr.Dataset(
            {
                "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), np.ones((1, 2, n, n))),
                "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), np.full((1, 2, n, n), 33.5)),
                "zeta": (("eta_rho", "xi_rho"), np.zeros((n, n))),
                "h": (("eta_rho", "xi_rho"), np.full((n, n), 100.0)),
                "mask_rho": (("eta_rho", "xi_rho"), np.ones((n, n))),
                "lat_rho": (("eta_rho", "xi_rho"), np.linspace(33.0, 33.3, n)[:, None] * np.ones((n, n))),
                "lon_rho": (("eta_rho", "xi_rho"), np.linspace(-120.5, -120.2, n)[None, :] * np.ones((n, n))),
                "pm": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
                "pn": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
                "hc": 50.0,
                "s_rho": ("s_rho", np.array([-0.75, -0.25])),
                "Cs_r": ("s_rho", np.array([-0.5, 0.0])),
            }
        )

    def glorys_fetch(_day: dt.date) -> dict:
        raise RuntimeError("simulated GLORYS fetch failure")

    with pytest.raises(RuntimeError, match="simulated GLORYS"):
        run_overlap_pairing(
            config=cfg,
            days=[dt.date(2024, 9, 1)],
            wcofs_open=wcofs_open,
            glorys_fetch=glorys_fetch,
        )
    assert not glorys_log.exists()
