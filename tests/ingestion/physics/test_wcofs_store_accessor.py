"""Public read-only WCOFS processed store accessor (no network)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from fishai.ingestion.physics.wcofs_store import package_wcofs_cycle, write_wcofs_cycle
from fishai.ingestion.sources import attribution_for
from fishai.ingestion.physics.wcofs_pull_log import build_day_tombstone_record
from fishai.ingestion.physics.wcofs_pull_log import append_pull_log, pull_log_path, resolve_pull_log_dir
from fishai.physics.store import (
    CycleNotAvailable,
    WcofsDayFailed,
    latest_wcofs_cycle_date,
    list_wcofs_cycles,
    open_wcofs_cycle,
)


def _snapshot_files(root: Path) -> dict[str, tuple[int, int]]:
    return {
        str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }


def _synthetic_merged(n_s: int = 4, n_eta: int = 3, n_xi: int = 3) -> xr.Dataset:
    s_rho = (np.arange(1, n_s + 1) - n_s - 0.5) / n_s
    lat = np.linspace(33.0, 33.1, n_eta)
    lon = np.linspace(-120.0, -119.9, n_xi)
    lat2d = np.broadcast_to(lat[:, None], (n_eta, n_xi))
    lon2d = np.broadcast_to(lon[None, :], (n_eta, n_xi))
    h = np.full((n_eta, n_xi), 100.0)
    temp = np.linspace(10, 18, n_s)[:, None, None] * np.ones((n_s, n_eta, n_xi))
    salt = np.full((n_s, n_eta, n_xi), 33.5)
    base = xr.Dataset(
        {
            "temp": (("s_rho", "eta_rho", "xi_rho"), temp),
            "salt": (("s_rho", "eta_rho", "xi_rho"), salt),
            "zeta": (("eta_rho", "xi_rho"), np.zeros((n_eta, n_xi))),
            "h": (("eta_rho", "xi_rho"), h),
            "mask_rho": (("eta_rho", "xi_rho"), np.ones((n_eta, n_xi))),
            "lat_rho": (("eta_rho", "xi_rho"), lat2d),
            "lon_rho": (("eta_rho", "xi_rho"), lon2d),
            "hc": 50.0,
            "s_rho": ("s_rho", s_rho),
            "Cs_r": ("s_rho", np.linspace(-1, 0, n_s)),
        }
    )
    merged = base.expand_dims(lead_hours=[3])
    merged.attrs["attribution"] = attribution_for("wcofs")
    merged.attrs["source"] = "wcofs"
    return merged


def test_open_wcofs_cycle_schema_and_attrs(tmp_path: Path) -> None:
    cycle = dt.date(2026, 9, 28)
    write_wcofs_cycle(_synthetic_merged(), cycle, tmp_path)
    ds = open_wcofs_cycle(cycle, store_root=tmp_path)
    assert ds.attrs["cycle_id"] == "20260928T03Z"
    assert ds.attrs["source"] == "wcofs"
    assert "WCOFS" in ds.attrs["attribution"]
    assert "z" in ds and ds["z"].attrs.get("positive") == "down"
    assert "T3m" in ds and "MLD_m" in ds and "lat" in ds and "lon" in ds
    assert "lead_hours" in ds.dims


def test_missing_cycle_raises(tmp_path: Path) -> None:
    with pytest.raises(CycleNotAvailable):
        open_wcofs_cycle(dt.date(1999, 1, 1), store_root=tmp_path)


def test_list_wcofs_cycles(tmp_path: Path) -> None:
    write_wcofs_cycle(_synthetic_merged(), dt.date(2026, 1, 2), tmp_path)
    write_wcofs_cycle(_synthetic_merged(), dt.date(2026, 1, 5), tmp_path)
    assert list_wcofs_cycles(tmp_path) == [dt.date(2026, 1, 2), dt.date(2026, 1, 5)]


def test_open_never_calls_network(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(*_a, **_k):
        raise AssertionError("network must not be used by open_wcofs_cycle")

    monkeypatch.setattr("fishai.ingestion.physics.http_util.get_bytes", _boom)
    monkeypatch.setattr("fishai.ingestion.physics.http_util.head_ok", _boom)
    cycle = dt.date(2026, 9, 1)
    path = write_wcofs_cycle(_synthetic_merged(), cycle, tmp_path)
    before = _snapshot_files(path)
    ds = open_wcofs_cycle(cycle, store_root=tmp_path, variables=["T3m", "MLD_m"], lead_hours=[3])
    assert "T3m" in ds
    assert _snapshot_files(path) == before


def test_package_wcofs_cycle_depth_positive_down() -> None:
    packaged = package_wcofs_cycle(_synthetic_merged(), dt.date(2026, 9, 28))
    assert float(packaged["z"].min()) >= 0


def test_tombstoned_day_raises_without_falling_back_to_older_zarr(tmp_path: Path) -> None:
    prev = dt.date(2026, 9, 27)
    failed = dt.date(2026, 9, 28)
    write_wcofs_cycle(_synthetic_merged(), prev, tmp_path)
    log_dir = resolve_pull_log_dir(tmp_path)
    log_path = pull_log_path(failed.strftime("%Y%m%d"), log_dir=log_dir)
    append_pull_log(
        build_day_tombstone_record(failed, reason="wcofs_nowcast_missing"),
        log_path=log_path,
    )
    with pytest.raises(WcofsDayFailed) as excinfo:
        open_wcofs_cycle(failed, store_root=tmp_path)
    assert excinfo.value.reason == "wcofs_nowcast_missing"
    with pytest.raises(WcofsDayFailed):
        latest_wcofs_cycle_date(tmp_path, as_of=failed)
    open_wcofs_cycle(prev, store_root=tmp_path)
