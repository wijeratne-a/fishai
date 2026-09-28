"""Shared in-memory WCOFS NetCDF bytes for physics ingestion tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import netCDF4 as nc
import numpy as np


def write_mini_wcofs_bytes(n_eta: int = 6, n_xi: int = 6, n_s: int = 4) -> bytes:
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
