"""WCOFS hourly UTC mean overlap counting and bbox slice helpers (no network in CI)."""

from __future__ import annotations

import datetime as dt

import numpy as np

from fishai.ingestion.physics.wcofs_utc_daily_s3 import (
    eta_xi_slices_for_bbox,
    unique_fields_files_for_utc_days,
)


def test_unique_fields_files_dedupe_across_days() -> None:
    d0 = dt.date(2024, 9, 1)
    d1 = dt.date(2024, 9, 2)
    refs = unique_fields_files_for_utc_days([d0, d1])
    assert len(refs) == 48
    keys = {r.as_tuple() for r in refs}
    assert len(keys) == 48


def test_eta_xi_slices_for_pilot_bbox() -> None:
    lat = np.array([[33.0, 33.0], [34.0, 34.0]])
    lon = np.array([[-120.0, -118.0], [-120.0, -118.0]])
    js, ie = eta_xi_slices_for_bbox(lat, lon, (32.5, 34.5, -121.0, -117.0))
    assert js == slice(0, 2)
    assert ie == slice(0, 2)
