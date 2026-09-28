"""WCOFS PDS key resolution and open (mocked listings; no network)."""

from __future__ import annotations

import datetime as dt
import io

import netCDF4 as nc
import numpy as np
import pytest
import xarray as xr

from fishai.ingestion.physics.wcofs_pds_store import (
    CycleNotAvailable,
    avg_nowcast_basename,
    fields_basename_candidates,
    layout_prefixes,
    open_wcofs_cycle,
    resolve_avg_nowcast_key,
    resolve_fields_key,
)


def _listing_map(prefix_to_keys: dict[str, list[str]]):
    def list_keys(prefix: str) -> list[str]:
        return prefix_to_keys.get(prefix, [])

    return list_keys


def test_layout_prefixes_daily_monthly_and_yyyymm() -> None:
    day = dt.date(2025, 1, 10)
    prefixes = layout_prefixes(day)
    assert prefixes[0].endswith("2025/01/10/")
    assert any(p.endswith("2025/01/") for p in prefixes)
    legacy = layout_prefixes(dt.date(2024, 8, 15))
    assert legacy[0].endswith("202408/")


def test_resolve_old_style_yyyymm_layout() -> None:
    day = dt.date(2024, 8, 1)
    _, old = fields_basename_candidates(day, "n003")
    prefix = f"wcofs/netcdf/{day:%Y%m}/"
    key = f"{prefix}{old}"
    resolved = resolve_fields_key(day, "n003", _listing_map({prefix: [key]}))
    assert resolved == key


def test_resolve_new_style_daily_layout() -> None:
    day = dt.date(2025, 3, 4)
    new, _ = fields_basename_candidates(day, "n006")
    prefix = f"wcofs/netcdf/{day:%Y/%m/%d}/"
    key = f"{prefix}{new}"
    resolved = resolve_fields_key(day, "n006", _listing_map({prefix: [key]}))
    assert resolved.endswith(new)


def test_overlap_week_prefers_new_style() -> None:
    day = dt.date(2024, 9, 5)
    new, old = fields_basename_candidates(day, "n003")
    prefix = f"wcofs/netcdf/{day:%Y%m}/"
    keys = [f"{prefix}{old}", f"{prefix}{new}"]
    resolved = resolve_fields_key(day, "n003", _listing_map({prefix: keys}))
    assert resolved.endswith(new)


def test_missing_cycle_raises() -> None:
    day = dt.date(2020, 1, 1)
    with pytest.raises(CycleNotAvailable):
        resolve_fields_key(day, "n003", _listing_map({}))


def test_avg_nowcast_resolution() -> None:
    day = dt.date(2024, 9, 1)
    base = avg_nowcast_basename(day)
    prefix = f"wcofs/netcdf/{day:%Y%m}/"
    key = f"{prefix}{base}"
    assert resolve_avg_nowcast_key(day, _listing_map({prefix: [key]})) == key


def _mini_nc_bytes(parallel_mode: bool = False) -> bytes:
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp:
        tmp_path = tmp.name
    with nc.Dataset(tmp_path, mode="w") as ds:
        ds.createDimension("ocean_time", 1)
        ds.createDimension("s_rho", 2)
        ds.createDimension("eta_rho", 2)
        ds.createDimension("xi_rho", 2)
        if parallel_mode:
            ds.title = "WCOFS parallel mode test"
        for name in ("lat_rho", "lon_rho", "h", "mask_rho", "zeta"):
            v = ds.createVariable(name, "f8", ("eta_rho", "xi_rho"))
            v[:] = 1.0
        ds.createVariable("hc", "f8")[:] = 50.0
        ds.createVariable("s_rho", "f8", ("s_rho",))[:] = [-0.25, -0.75]
        temp = ds.createVariable("temp", "f8", ("ocean_time", "s_rho", "eta_rho", "xi_rho"))
        salt = ds.createVariable("salt", "f8", ("ocean_time", "s_rho", "eta_rho", "xi_rho"))
        temp[0] = 15.0
        salt[0] = 33.0
    data = Path(tmp_path).read_bytes()
    Path(tmp_path).unlink(missing_ok=True)
    return data


def test_open_rejects_parallel_mode_july_2024() -> None:
    day = dt.date(2024, 7, 15)
    new, _ = fields_basename_candidates(day, "n003")
    prefix = layout_prefixes(day)[0]
    key = f"{prefix}{new}"
    payload = _mini_nc_bytes(parallel_mode=True)

    def list_keys(_prefix: str) -> list[str]:
        return [key]

    def get_bytes(_url: str, **kwargs) -> bytes:  # noqa: ARG001
        return payload

    with pytest.raises(CycleNotAvailable, match="parallel"):
        open_wcofs_cycle(day, list_keys=list_keys, get_bytes=get_bytes, head_ok=lambda _u: True)


def test_open_wcofs_cycle_returns_dataset() -> None:
    day = dt.date(2026, 1, 3)
    new, _ = fields_basename_candidates(day, "n003")
    prefix = layout_prefixes(day)[0]
    key = f"{prefix}{new}"
    payload = _mini_nc_bytes()

    ds = open_wcofs_cycle(
        day,
        list_keys=lambda _p: [key],
        get_bytes=lambda _u, **k: payload,
        head_ok=lambda _u: True,
    )
    assert isinstance(ds, xr.Dataset)
    assert "temp" in ds
