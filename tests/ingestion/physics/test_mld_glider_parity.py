"""MLD parity between glider profiles and model grid columns."""

from __future__ import annotations

import numpy as np

from fishai.ingestion.physics.vertical import MLD_NOT_REACHED, mld, mld_from_profile
from fishai.ingestion.sensors.internal.holdout import mixed_layer_depth


def test_glider_and_model_mld_match_on_synthetic_profile() -> None:
    depths = np.array([0.0, 10.0, 20.0, 30.0, 50.0])
    temps = np.array([20.0, 19.9, 18.0, 15.0, 12.0])
    glider_mld, reason = mld_from_profile(depths, temps)
    assert reason is None
    assert glider_mld == mixed_layer_depth(depths, temps)

    zz = -depths[::-1]
    tt = temps[::-1]
    grid_mld = mld(zz[:, None, None], tt[:, None, None])[0, 0]
    assert np.isclose(grid_mld, glider_mld)


def test_mld_not_reached_when_no_02c_drop() -> None:
    depths = np.array([0.0, 10.0, 20.0, 30.0])
    temps = np.array([20.0, 19.95, 19.9, 19.85])
    depth_m, reason = mld_from_profile(depths, temps)
    assert depth_m is None
    assert reason == MLD_NOT_REACHED
    z = -depths
    assert np.isnan(mld(z[:, None, None], temps[:, None, None])[0, 0])
