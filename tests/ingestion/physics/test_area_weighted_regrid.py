"""True area-weighted coarsening onto the GLORYS grid."""

from __future__ import annotations

import numpy as np

from fishai.ingestion.physics.harmonize import (
    area_weighted_regrid,
    assign_glorys_cell_indices,
    glorys_target_grid,
)


def test_area_weighted_mean_unequal_cell_areas() -> None:
    lats, lons = glorys_target_grid(33.0, 33.0, -120.0, -120.0, resolution_deg=0.1)
    lat_s = np.array([33.0, 33.0])
    lon_s = np.array([-120.0, -120.0])
    field = np.array([10.0, 20.0])
    area = np.array([1.0, 3.0])
    out, wf = area_weighted_regrid(
        field,
        lat_s,
        lon_s,
        lats,
        lons,
        cell_area=area,
        min_wet_fraction=0.0,
        resolution_deg=0.1,
    )
    assert wf[0, 0] == 1.0
    assert abs(out[0, 0] - 17.5) < 1e-9


def test_half_open_lon_edge_assigns_to_western_cell() -> None:
    lats, lons = glorys_target_grid(33.0, 33.0, -120.1, -119.9, resolution_deg=0.1)
    dlon = float(np.median(np.diff(lons)))
    edge_lon = float(lons[0] + dlon / 2.0)
    lat_s = np.array([33.0, 33.0])
    lon_s = np.array([edge_lon, edge_lon + 1e-6])
    j_idx, i_idx = assign_glorys_cell_indices(
        lat_s, lon_s, lats, lons, resolution_deg=0.1
    )
    assert i_idx[0] == 1
    assert i_idx[1] == 1


def test_deep_cell_cannot_fill_mostly_shallow_box() -> None:
    """One deep wet cell must not represent a box that is mostly too shallow."""
    lats, lons = glorys_target_grid(33.0, 33.0, -120.0, -120.0, resolution_deg=0.2)
    lat_s = np.array([33.0, 33.0, 33.0])
    lon_s = np.array([-120.05, -120.0, -119.95])
    field = np.array([99.0, 99.0, 5.0])
    area = np.array([10.0, 10.0, 1.0])
    wet = np.array([True, True, True])
    depth_reachable = np.array([False, False, True])
    out, wf = area_weighted_regrid(
        field,
        lat_s,
        lon_s,
        lats,
        lons,
        wet_mask=wet,
        cell_area=area,
        depth_reachable=depth_reachable,
        min_wet_fraction=0.5,
        resolution_deg=0.2,
    )
    assert wf[0, 0] < 0.5
    assert np.isnan(out[0, 0])
