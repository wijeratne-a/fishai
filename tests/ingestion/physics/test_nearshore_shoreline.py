"""Nearshore flag using vendored Natural Earth shoreline."""

from __future__ import annotations

import numpy as np

from fishai.ingestion.physics.coast_distance import distance_to_shoreline_km, nearshore_mask, shoreline_path_from_config
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config


def test_catalina_nearshore_open_ocean_not() -> None:
    cfg = load_overlap_config()
    shore = shoreline_path_from_config(cfg)
    assert shore.is_file()
    # ~5 km offshore of Santa Catalina Island (southwest of Avalon)
    near_island = (33.34, -118.48)
    open_ocean = (31.8, -121.2)
    d_near = distance_to_shoreline_km(
        np.array([near_island[0]]),
        np.array([near_island[1]]),
        geojson_path=shore,
        densify_km=float(cfg["shoreline"]["densify_spacing_km"]),
    )[0]
    d_far = distance_to_shoreline_km(
        np.array([open_ocean[0]]),
        np.array([open_ocean[1]]),
        geojson_path=shore,
        densify_km=float(cfg["shoreline"]["densify_spacing_km"]),
    )[0]
    assert d_near <= float(cfg["nearshore_km"])
    assert d_far > 60.0
    mask_near = nearshore_mask(
        np.array([[near_island[0]]]),
        np.array([[near_island[1]]]),
        config=cfg,
    )
    mask_far = nearshore_mask(
        np.array([[open_ocean[0]]]),
        np.array([[open_ocean[1]]]),
        config=cfg,
    )
    assert bool(mask_near[0, 0])
    assert not bool(mask_far[0, 0])
