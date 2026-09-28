"""Recorded WCOFS nowcast gaps in the fit window (PR #14 / auditor ruling)."""

from __future__ import annotations

import datetime as dt

import numpy as np
import pytest
import xarray as xr

from fishai.ingestion.physics.wcofs_avg_nowcast_availability import (
    REASON_WCOFS_NOWCAST_MISSING,
    WcofsNowcastMissingDayError,
    assert_wcofs_nowcast_available,
    wcofs_nowcast_missing_fit_days,
)
from fishai.ingestion.physics.wcofs_glorys_grid import EVIDENCE_STATE_UNKNOWN
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    build_overlap_metadata,
    glorys_grid_from_config,
    load_overlap_config,
    run_overlap_pairing,
)
from fishai.ingestion.physics.wcofs_utc_daily_pairing import valid_time_utc_for_cycle_lead


def _fields_slab(cycle: dt.date, lead: str) -> xr.Dataset:
    when = valid_time_utc_for_cycle_lead(cycle, lead)
    n = 3
    temp = np.full((1, n, 2, 2), 15.0, dtype=float)
    return xr.Dataset(
        {
            "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp),
            "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp + 10),
            "zeta": (("eta_rho", "xi_rho"), np.zeros((2, 2))),
            "h": (("eta_rho", "xi_rho"), np.full((2, 2), 100.0)),
            "mask_rho": (("eta_rho", "xi_rho"), np.ones((2, 2))),
            "lat_rho": (("eta_rho", "xi_rho"), np.full((2, 2), 33.5)),
            "lon_rho": (("eta_rho", "xi_rho"), np.full((2, 2), -120.0)),
            "pm": (("eta_rho", "xi_rho"), np.full((2, 2), 1.0 / 3000.0)),
            "pn": (("eta_rho", "xi_rho"), np.full((2, 2), 1.0 / 3000.0)),
            "hc": 50.0,
            "s_rho": ("s_rho", (np.arange(1, 4) - 4 - 0.5) / 4),
            "Cs_r": ("s_rho", np.linspace(-1, 0, 3)),
        },
        coords={"ocean_time": [np.datetime64(when.strftime("%Y-%m-%dT%H:%M:%S"))]},
    )


def test_recorded_fit_gap_count_and_dates() -> None:
    cfg = load_overlap_config()
    missing = wcofs_nowcast_missing_fit_days(cfg)
    assert len(missing) == 44
    assert dt.date(2024, 9, 5) in missing
    assert dt.date(2024, 9, 6) in missing
    assert dt.date(2024, 11, 20) in missing
    assert dt.date(2024, 12, 31) in missing
    assert dt.date(2024, 11, 19) not in missing
    assert dt.date(2025, 1, 1) not in missing


def test_assert_wcofs_nowcast_available_raises_with_auditor_reason() -> None:
    cfg = load_overlap_config()
    with pytest.raises(WcofsNowcastMissingDayError) as excinfo:
        assert_wcofs_nowcast_available(dt.date(2024, 9, 5), cfg)
    assert excinfo.value.reason_code == REASON_WCOFS_NOWCAST_MISSING
    assert excinfo.value.evidence_state == EVIDENCE_STATE_UNKNOWN


def test_overlap_metadata_lists_missing_fit_days_with_reason() -> None:
    cfg = load_overlap_config()
    meta = build_overlap_metadata(cfg)
    records = meta["wcofs_nowcast_missing_fit_days"]
    assert len(records) == 44
    assert all(r["reason_code"] == REASON_WCOFS_NOWCAST_MISSING for r in records)
    assert all(r["evidence_state"] == EVIDENCE_STATE_UNKNOWN for r in records)
    assert records[0]["product"] == "avg.nowcast"


def test_missing_nowcast_days_excluded_from_pairing_counts(tmp_path) -> None:
    cfg = load_overlap_config()
    cfg = dict(cfg)
    cfg["pilot_bbox"] = {
        "lat_min": 33.0,
        "lat_max": 33.3,
        "lon_min": -120.5,
        "lon_max": -120.2,
    }
    cfg["coverage_report"] = {
        **cfg.get("coverage_report", {}),
        "json_path": str(tmp_path / "coverage_report.json"),
        "csv_path": str(tmp_path / "coverage_cells.csv"),
    }
    cfg["pull_logs"] = {
        "wcofs": str(tmp_path / "wcofs_pull_log.jsonl"),
        "glorys": str(tmp_path / "copernicus_pull_log.jsonl"),
    }
    missing_day = dt.date(2024, 9, 5)
    paired_day = dt.date(2024, 9, 7)
    z_levels = np.array([0.0, 3.0, 10.0])
    glorys_days: list[dt.date] = []

    def open_fields_lead(cycle: dt.date, lead: str) -> xr.Dataset:
        return _fields_slab(cycle, lead)

    def glorys_fetch(day: dt.date) -> dict:
        glorys_days.append(day)
        la, lo = glorys_grid_from_config(cfg)
        nj, ni = la.size, lo.size
        nz = z_levels.size
        return {
            "thetao": 14.0 + 0.1 * z_levels[:, None, None] * np.ones((nz, nj, ni)),
            "so": np.full((nz, nj, ni), 33.5),
            "depth": z_levels,
        }

    _df, meta = run_overlap_pairing(
        config=cfg,
        days=[missing_day, paired_day],
        open_fields_lead=open_fields_lead,
        glorys_fetch=glorys_fetch,
    )
    assert missing_day not in glorys_days
    assert glorys_days == [paired_day]
    assert meta["overlap_pairing_days_requested"] == 2
    assert meta["overlap_pairing_days_paired"] == 1
    assert meta["overlap_pairing_days_skipped_wcofs_nowcast_missing"] == 1
    skipped = meta["wcofs_nowcast_missing_days"]
    assert len(skipped) == 1
    assert skipped[0]["day"] == missing_day.isoformat()
    assert skipped[0]["reason_code"] == REASON_WCOFS_NOWCAST_MISSING
    assert skipped[0]["evidence_state"] == EVIDENCE_STATE_UNKNOWN
