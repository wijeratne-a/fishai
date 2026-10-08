"""MLD on coarsened WCOFS columns is finite when the profile reaches 10 m."""

from __future__ import annotations

import numpy as np

from fishai.ingestion.physics.wcofs_glorys_grid import (
    WcofsGlorysGrid,
    compute_wcofs_covariates_on_glorys_grid,
)


def test_mld_uses_shallow_first_column_and_ignores_nan_below_bottom():
    depth = np.arange(0, 201, dtype=float)
    temp = np.full((2, 2, depth.size), np.nan)
    # 15 C through 20 m, then a 0.05 C/m drop; rock below 80 m.
    for k, z in enumerate(depth):
        if z <= 20:
            temp[0, 0, k] = 15.0
        elif z <= 80:
            temp[0, 0, k] = 15.0 - 0.05 * (z - 20.0)
    salt = np.where(np.isfinite(temp), 33.5, np.nan)
    wet = np.isfinite(temp).astype(float)
    gridded = WcofsGlorysGrid(
        lat=np.array([33.0, 33.08]),
        lon=np.array([-118.0, -117.92]),
        depth_m=depth,
        temp=temp,
        salt=salt,
        wet_fraction=wet,
    )
    fields = compute_wcofs_covariates_on_glorys_grid(gridded)
    mld_m = float(fields["MLD_m"][0, 0])
    assert np.isfinite(mld_m)
    assert 20.0 < mld_m < 40.0
