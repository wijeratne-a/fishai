"""Vertical coordinate and MLD tests (synthetic, no network)."""

from __future__ import annotations

import numpy as np

from fishai.ingestion.physics.vertical import cs_r_vstretching4, mld, s_to_z, thermocline_depth


def test_s_to_z_matches_vtransform2_formula() -> None:
    n = 5
    s_rho = (np.arange(1, n + 1) - n - 0.5) / n
    cs_r = cs_r_vstretching4(s_rho, theta_s=8.0, theta_b=3.0)
    h = np.array([[100.0]])
    zeta = np.array([[0.0]])
    hc = 50.0
    z = s_to_z(h, zeta, s_rho, hc, cs_r=cs_r)
    for k, sk in enumerate(s_rho):
        s_val = (hc * sk + 100.0 * cs_r[k]) / (hc + 100.0)
        expected = 0.0 + (0.0 + 100.0) * s_val
        assert abs(z[k, 0, 0] - expected) < 1e-10


def test_mld_synthetic_profile() -> None:
    # Surface-last ROMS ordering (k increases upward): bottom -> surface
    depths = np.array([-50.0, -20.0, -10.0, -5.0, 0.0])
    temps = np.array([10.0, 15.0, 17.8, 17.9, 18.0])
    z = depths[:, None, None]
    t = temps[:, None, None]
    mld_out = mld(z, t, dT=0.2, zref_m=10.0)
    assert 10.0 < float(mld_out[0, 0]) < 25.0


def test_thermocline_on_linear_gradient() -> None:
    z = np.linspace(-200.0, 0.0, 40)[:, None, None]
    temp = (z + 200.0) / 10.0
    tc = thermocline_depth(z, temp, zmin_m=5.0, zmax_m=300.0, min_grad=0.001)
    assert np.isfinite(tc[0, 0])
