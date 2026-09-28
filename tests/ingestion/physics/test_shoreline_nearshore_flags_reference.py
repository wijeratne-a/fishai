"""Vendored shoreline nearshore flags must match full-resolution Natural Earth reference."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fishai.ingestion.physics.coast_distance import nearshore_mask
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config

REFERENCE = (
    Path(__file__).resolve().parents[2] / "fixtures" / "shoreline_nearshore_flags_reference.csv"
)


def test_vendored_nearshore_flags_match_full_resolution_reference() -> None:
    cfg = load_overlap_config()
    ref = pd.read_csv(REFERENCE)
    lat = ref["lat"].to_numpy(dtype=float)
    lon = ref["lon"].to_numpy(dtype=float)
    expected = ref["nearshore"].to_numpy(dtype=int)
    vendored = nearshore_mask(lat, lon, config=cfg).astype(int)
    np.testing.assert_array_equal(vendored, expected)
