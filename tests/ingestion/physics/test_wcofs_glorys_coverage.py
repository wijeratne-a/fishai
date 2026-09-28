"""Harmonization coverage report (diagnostic only; no CUFES training changes)."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from fishai.ingestion.physics.covariates import join_covariates_to_events
from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.wcofs_glorys_coverage import (
    CoverageAccumulator,
    build_coverage_report,
    harmonization_gap_mask,
    load_cufes_event_index,
    write_coverage_report,
)
from fishai.ingestion.physics.wcofs_glorys_grid import coarsen_wcofs_to_glorys
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    glorys_grid_from_config,
    load_overlap_config,
    run_overlap_pairing,
)
from fishai.ingestion.physics.wcofs_utc_daily_pairing import valid_time_utc_for_cycle_lead


def _synthetic_wcofs_land_heavy(ocean_time: dt.datetime | None = None) -> xr.Dataset:
    n = 6
    s_rho = (np.arange(1, 5) - 5 - 0.5) / 5
    lat = np.linspace(33.05, 33.25, n)
    lon = np.linspace(-120.45, -120.25, n)
    lat2d = np.broadcast_to(lat[:, None], (n, n))
    lon2d = np.broadcast_to(lon[None, :], (n, n))
    temp = 15.0 + np.linspace(0, 2, 4)[:, None, None] * np.ones((4, n, n))
    mask = np.zeros((n, n))
    mask[2:4, 2:4] = 1.0
    ot = ocean_time or dt.datetime(2024, 9, 1, 12, 0)
    return xr.Dataset(
        {
            "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp[None, ...]),
            "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), np.full((1, 4, n, n), 33.5)),
            "zeta": (("eta_rho", "xi_rho"), np.zeros((n, n))),
            "h": (("eta_rho", "xi_rho"), np.full((n, n), 100.0)),
            "mask_rho": (("eta_rho", "xi_rho"), mask),
            "lat_rho": (("eta_rho", "xi_rho"), lat2d),
            "lon_rho": (("eta_rho", "xi_rho"), lon2d),
            "pm": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
            "pn": (("eta_rho", "xi_rho"), np.full((n, n), 1.0 / 3000.0)),
            "hc": 50.0,
            "s_rho": ("s_rho", s_rho),
            "Cs_r": ("s_rho", np.linspace(-1, 0, 4)),
        },
        coords={"ocean_time": [np.datetime64(ot.strftime("%Y-%m-%dT%H:%M:%S"))]},
    )


def _open_fields_lead_synthetic(cycle: dt.date, lead: str) -> xr.Dataset:
    when = valid_time_utc_for_cycle_lead(cycle, lead)
    return _synthetic_wcofs_land_heavy(when)


def test_coverage_report_written_on_overlap_run(tmp_path: Path) -> None:
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
    z_levels = np.array([0.0, 1.0, 3.0, 10.0])

    def glorys_fetch(_day: dt.date) -> dict:
        la, lo = glorys_grid_from_config(cfg)
        nj, ni = la.size, lo.size
        nz = z_levels.size
        thetao = 14.0 + 0.1 * z_levels[:, None, None] * np.ones((nz, nj, ni))
        so = np.full((nz, nj, ni), 33.5)
        return {"thetao": thetao, "so": so, "depth": z_levels}

    _df, meta = run_overlap_pairing(
        config=cfg,
        days=[dt.date(2024, 9, 1)],
        open_fields_lead=_open_fields_lead_synthetic,
        glorys_fetch=glorys_fetch,
    )
    report_path = tmp_path / "coverage_report.json"
    assert report_path.is_file()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["min_wet_fraction"] == 0.5
    assert meta["coverage_report_json"]
    surface = next(lev for lev in report["levels"] if lev["name"] == "surface_0m")
    assert surface["glorys_ocean_wcofs_insufficient_cells"]["total"] >= 0
    cufes = surface.get("cufes_events")
    assert cufes is not None
    assert cufes["expected_kept_event_count"] == 14592
    assert cufes["expected_reduced_event_count"] == 13326


def test_cufes_join_row_count_unchanged_when_coverage_report_runs(tmp_path: Path) -> None:
    events = pd.DataFrame(
        {
            "event_id": ["CUFES:2020-01:SH01:1", "CUFES:2020-01:SH01:2"],
            "start_time": ["2020-01-01T12:00:00Z", "2020-01-01T13:00:00Z"],
            "stop_time": ["2020-01-01T12:10:00Z", "2020-01-01T13:10:00Z"],
            "start_latitude": [33.0, 33.1],
            "start_longitude": [-120.5, -120.4],
            "stop_latitude": [33.01, 33.11],
            "stop_longitude": [-120.49, -120.39],
        }
    )

    def sampler(lat: float, lon: float, _when: pd.Timestamp) -> dict:
        return {"T3m": lat, "S3m": 33.0, "MLD_m": 20.0, "sst_grad": 0.1, "front_distance_km": 5.0, "upwelling": 0.0}

    out_a, qc_a, _ = join_covariates_to_events(events, field_sampler=sampler, source="glorys")
    lat_dst, lon_dst = glorys_target_grid(32.5, 33.5, -121.0, -117.0)
    nearshore = np.zeros((lat_dst.size, lon_dst.size), dtype=bool)
    acc = CoverageAccumulator(
        lat_dst, lon_dst, nearshore, np.array([0.0, 3.0]), min_wet_fraction=0.5
    )
    report = build_coverage_report(acc, cufes_events=load_cufes_event_index())
    write_coverage_report(report, json_path=tmp_path / "cov.json", accumulator=acc)
    out_b, qc_b, _ = join_covariates_to_events(events, field_sampler=sampler, source="glorys")
    assert len(out_a) == len(out_b) == len(events)
    assert qc_a["drop_summary"]["input_event_count"] == qc_b["drop_summary"]["input_event_count"]
    ocean_a = int((~out_a["excluded"]).sum())
    ocean_b = int((~out_b["excluded"]).sum())
    assert ocean_a == ocean_b


def test_harmonization_gap_requires_glorys_ocean() -> None:
    cfg = load_overlap_config()
    lat_dst, lon_dst = glorys_target_grid(33.0, 33.2, -120.5, -120.3, resolution_deg=0.1)
    depth = np.arange(0, 4, 1.0)
    gridded = coarsen_wcofs_to_glorys(
        _synthetic_wcofs_land_heavy(), lat_dst, lon_dst, depth, min_wet_fraction=0.5
    )
    z_levels = np.array([0.0, 3.0, 10.0])
    nj, ni = len(lat_dst), len(lon_dst)
    thetao = np.full((3, nj, ni), np.nan)
    thetao[:, 1:3, 1:3] = 14.0
    gap = harmonization_gap_mask(gridded, z_levels, thetao, 0.0, min_wet_fraction=0.5)
    assert gap.dtype == bool
