"""WCOFS×GLORYS overlap pairing on synthetic grids (no network)."""

from __future__ import annotations

import datetime as dt

import numpy as np
import xarray as xr

from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    depth_grid_m,
    load_overlap_config,
    meteorological_season,
    overlap_dates,
    pair_overlap_from_synthetic,
    split_label,
)


def _synthetic_wcofs(n_eta: int = 4, n_xi: int = 4, n_s: int = 5) -> xr.Dataset:
    s_rho = (np.arange(1, n_s + 1) - n_s - 0.5) / n_s
    lat = np.linspace(33.0, 33.3, n_eta)
    lon = np.linspace(-120.5, -120.2, n_xi)
    lat2d = np.broadcast_to(lat[:, None], (n_eta, n_xi))
    lon2d = np.broadcast_to(lon[None, :], (n_eta, n_xi))
    temp = np.linspace(12, 18, n_s)[:, None, None] * np.ones((n_s, n_eta, n_xi))
    salt = np.full((n_s, n_eta, n_xi), 33.5)
    return xr.Dataset(
        {
            "temp": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), temp[None, ...]),
            "salt": (("ocean_time", "s_rho", "eta_rho", "xi_rho"), salt[None, ...]),
            "zeta": (("eta_rho", "xi_rho"), np.zeros((n_eta, n_xi))),
            "h": (("eta_rho", "xi_rho"), np.full((n_eta, n_xi), 120.0)),
            "mask_rho": (("eta_rho", "xi_rho"), np.ones((n_eta, n_xi))),
            "lat_rho": (("eta_rho", "xi_rho"), lat2d),
            "lon_rho": (("eta_rho", "xi_rho"), lon2d),
            "pm": (("eta_rho", "xi_rho"), np.full((n_eta, n_xi), 1.0 / 3500.0)),
            "pn": (("eta_rho", "xi_rho"), np.full((n_eta, n_xi), 1.0 / 3500.0)),
            "hc": 50.0,
            "s_rho": ("s_rho", s_rho),
            "Cs_r": ("s_rho", np.linspace(-1, 0, n_s)),
        }
    )


def test_overlap_config_day_count() -> None:
    cfg = load_overlap_config()
    days = overlap_dates(cfg)
    assert len(days) == int(cfg["overlap"]["expected_days"]) == 661


def test_split_and_season_labels() -> None:
    cfg = load_overlap_config()
    assert split_label(dt.date(2024, 9, 1), cfg) == "fit"
    assert split_label(dt.date(2025, 9, 1), cfg) == "test"
    assert meteorological_season(dt.date(2024, 12, 15)) == "winter"


def test_wcofs_cycle_for_glorys_day_is_next_day() -> None:
    cfg = load_overlap_config()
    assert cfg["wcofs"]["cycle_offset_days"] == 1
    glorys_day = dt.date(2024, 9, 2)
    from fishai.ingestion.physics.wcofs_glorys_overlap import wcofs_cycle_date_for_glorys_day

    assert wcofs_cycle_date_for_glorys_day(glorys_day, cfg) == dt.date(2024, 9, 3)


def test_overlap_pairing_logs_next_cycle_ocean_time(tmp_path) -> None:
    """Pairing opens WCOFS cycle D+1 and records that file's ocean_time."""
    import json

    import xarray as xr

    from fishai.ingestion.physics.wcofs_glorys_overlap import run_overlap_pairing

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
    cfg["coverage_report"] = {
        **cfg.get("coverage_report", {}),
        "json_path": str(tmp_path / "coverage_report.json"),
        "csv_path": str(tmp_path / "coverage_cells.csv"),
    }
    glorys_day = dt.date(2024, 9, 2)
    opened: list[dt.date] = []
    # 2024-09-02 15:00:00 UTC — realistic stamp for cycle 2024-09-03 (R minus 12 h).
    ocean_seconds = 273682800.0

    def wcofs_open(cycle: dt.date) -> xr.Dataset:
        opened.append(cycle)
        ds = _synthetic_wcofs()
        ds["ocean_time"] = ("ocean_time", np.array([ocean_seconds]))
        ds["ocean_time"].attrs["units"] = "seconds since 2016-01-01 00:00:00"
        ds.attrs["wcofs_s3_key"] = f"wcofs/netcdf/test/wcofs.t03z.{cycle:%Y%m%d}.avg.nowcast.nc"
        return ds

    def glorys_fetch(_day: dt.date) -> dict:
        from fishai.ingestion.physics.wcofs_glorys_overlap import glorys_grid_from_config

        lat_dst, lon_dst = glorys_grid_from_config(cfg)
        z_levels = np.array([0.494, 5.0, 10.0])
        nj, ni = len(lat_dst), len(lon_dst)
        nz = z_levels.size
        return {
            "thetao": np.full((nz, nj, ni), 15.0),
            "so": np.full((nz, nj, ni), 33.4),
            "depth": z_levels,
            "time_utc": "2024-09-02T12:00:00+00:00",
        }

    df, _meta = run_overlap_pairing(
        config=cfg,
        days=[glorys_day],
        wcofs_open=wcofs_open,
        glorys_fetch=glorys_fetch,
    )
    assert opened == [dt.date(2024, 9, 3)]
    assert set(df["wcofs_cycle_date"]) == {"2024-09-03"}
    assert set(df["day"]) == {"2024-09-02"}
    assert set(df["wcofs_ocean_time_utc"]) == {"2024-09-02T15:00:00+00:00"}
    assert set(df["glorys_time_utc"]) == {"2024-09-02T12:00:00+00:00"}
    log_path = tmp_path / "wcofs_glorys_ocean_time.jsonl"
    record = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert record["glorys_day"] == "2024-09-02"
    assert record["wcofs_cycle_date"] == "2024-09-03"
    assert record["wcofs_cycle_offset_days"] == 1
    assert record["wcofs_ocean_time_utc"] == "2024-09-02T15:00:00+00:00"
    pull = json.loads((tmp_path / "wcofs_pull_log.jsonl").read_text(encoding="utf-8").strip())
    assert pull["cycle_date"] == "2024-09-03"


def test_pair_overlap_synthetic_row_shape() -> None:
    cfg = load_overlap_config()
    lat_dst, lon_dst = glorys_target_grid(33.0, 33.4, -120.6, -120.1, resolution_deg=0.05)
    z_levels = np.array([0.0, 5.0, 10.0, 50.0])
    nj, ni = len(lat_dst), len(lon_dst)
    nz = z_levels.size
    thetao = 14.0 + 0.1 * z_levels[:, None, None] * np.ones((nz, nj, ni))
    so = 33.0 + 0.01 * z_levels[:, None, None] * np.ones((nz, nj, ni))
    day = dt.date(2024, 9, 2)
    df = pair_overlap_from_synthetic(
        day,
        _synthetic_wcofs(),
        thetao,
        so,
        z_levels,
        lat_dst,
        lon_dst,
        config=cfg,
    )
    assert len(df) == nj * ni
    assert "wcofs_T3m" in df.columns
    assert "glorys_T3m" in df.columns
    assert "wcofs_sst_grad" in df.columns
    assert "wcofs_front_distance_km" in df.columns
    assert "nearshore" in df.columns
    assert (df["split"] == "fit").all()
    grid = depth_grid_m(cfg)
    assert grid[0] == 0.0 and grid[-1] == 200.0 and grid[1] - grid[0] == 1.0
