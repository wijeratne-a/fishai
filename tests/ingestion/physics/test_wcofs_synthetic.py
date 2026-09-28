"""WCOFS fetch/subset tests with in-memory NetCDF (no network)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import netCDF4 as nc
import numpy as np
import pytest

from fishai.ingestion.physics.sources.wcofs import cycle_available, fetch_cycle


def _write_mini_wcofs_bytes(n_eta: int = 6, n_xi: int = 6, n_s: int = 4) -> bytes:
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp:
        tmp_path = tmp.name
    with nc.Dataset(tmp_path, mode="w") as ds:
        ds.createDimension("ocean_time", 1)
        ds.createDimension("s_rho", n_s)
        ds.createDimension("eta_rho", n_eta)
        ds.createDimension("xi_rho", n_xi)
        lat = np.linspace(32.5, 34.5, n_eta)
        lon = np.linspace(-120.5, -118.5, n_xi)
        lat2d = np.broadcast_to(lat[:, None], (n_eta, n_xi))
        lon2d = np.broadcast_to(lon[None, :], (n_eta, n_xi))
        for name, arr in (
            ("lat_rho", lat2d),
            ("lon_rho", lon2d),
            ("h", np.full((n_eta, n_xi), 200.0)),
            ("mask_rho", np.ones((n_eta, n_xi))),
            ("zeta", np.zeros((n_eta, n_xi))),
        ):
            v = ds.createVariable(name, "f8", ("eta_rho", "xi_rho"))
            v[:] = arr
        s_rho = (np.arange(1, n_s + 1) - n_s - 0.5) / n_s
        ds.createVariable("s_rho", "f8", ("s_rho",))[:] = s_rho
        ds.createVariable("Cs_r", "f8", ("s_rho",))[:] = np.linspace(-1.0, 0.0, n_s)
        ds.createVariable("hc", "f8")[:] = 50.0
        ds.createVariable("Vtransform", "i4")[:] = 2
        ds.createVariable("Vstretching", "i4")[:] = 4
        temp = ds.createVariable("temp", "f8", ("ocean_time", "s_rho", "eta_rho", "xi_rho"))
        salt = ds.createVariable("salt", "f8", ("ocean_time", "s_rho", "eta_rho", "xi_rho"))
        temp[0] = np.linspace(10, 18, n_s)[:, None, None]
        salt[0] = 33.0
        ot = ds.createVariable("ocean_time", "f8", ("ocean_time",))
        ot[:] = 0.0
    data = Path(tmp_path).read_bytes()
    Path(tmp_path).unlink(missing_ok=True)
    return data


def test_cycle_available_uses_injected_head() -> None:
    assert cycle_available(dt.date(2026, 9, 1), head_fn=lambda _u: True)
    assert not cycle_available(dt.date(2026, 9, 1), head_fn=lambda _u: False)


def test_fetch_cycle_subset_and_features() -> None:
    payload = _write_mini_wcofs_bytes()
    bbox = (32.0, 35.0, -121.0, -117.0)

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        return payload

    ds = fetch_cycle(
        dt.date(2026, 9, 28),
        ["n003"],
        bbox,
        get_fn=fake_get,
        head_fn=lambda _u: True,
    )
    assert "bottom_temp" in ds
    assert "mld_m" in ds
    assert ds.attrs["source"] == "wcofs"
