"""Shared in-memory WCOFS NetCDF bytes for physics ingestion tests."""

from __future__ import annotations

import datetime as dt
import tempfile
from pathlib import Path

import netCDF4 as nc
import numpy as np

from fishai.ingestion.physics.sources.wcofs import cycle_run_time, valid_time_for_lead_tag


def write_mini_wcofs_bytes(
    n_eta: int = 6,
    n_xi: int = 6,
    n_s: int = 4,
    *,
    cycle_date: dt.date | None = None,
    lead_tag: str = "n024",
    valid_time_shift_h: int = 0,
) -> bytes:
    cycle_date = cycle_date or dt.date(2026, 9, 26)
    valid = valid_time_for_lead_tag(cycle_date, lead_tag) + dt.timedelta(hours=valid_time_shift_h)
    epoch = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
    ocean_seconds = (valid - epoch).total_seconds()

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
        ot.units = "seconds since 1970-01-01 00:00:00 UTC"
        ot.calendar = "standard"
        ot[:] = ocean_seconds
    data = Path(tmp_path).read_bytes()
    Path(tmp_path).unlink(missing_ok=True)
    return data
