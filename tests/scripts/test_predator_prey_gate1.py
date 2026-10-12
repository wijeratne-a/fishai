"""Unit tests for GATE 1 overlap helpers (no network)."""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "predator_prey_gate1_overlap",
    _REPO / "scripts" / "predator_prey_gate1_overlap.py",
)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules[_spec.name] = _mod
_spec.loader.exec_module(_mod)

PredPoint = _mod.PredPoint
PreyEvent = _mod.PreyEvent
haversine_km = _mod.haversine_km
overlap_post_2010_only = _mod.overlap_post_2010_only
spatiotemporal_overlap = _mod.spatiotemporal_overlap


def test_haversine_zero_distance() -> None:
    assert haversine_km(33.0, -120.0, 33.0, -120.0) == 0.0


def test_post_2010_overlap_empty_when_predators_pre_2011() -> None:
    pred = [
        PredPoint(
            dataset_key="x",
            species="Phoebastria immutabilis",
            lat=33.5,
            lon=-120.0,
            when=datetime(2008, 6, 1, tzinfo=timezone.utc),
        )
    ]
    prey = [
        PreyEvent(
            source="swfsc_cps_trawl_haul_catch",
            species="jack_mackerel",
            lat=33.5,
            lon=-120.0,
            when=datetime(2020, 6, 1, tzinfo=timezone.utc),
            event_id="t:1",
        )
    ]
    all_years = spatiotemporal_overlap(pred, prey)
    assert all_years["n_pred_matched"] == 0
    post = overlap_post_2010_only(pred, prey)
    assert post["n_pred_pilot"] == 0
    assert post["n_pred_matched"] == 0


def test_spatiotemporal_match_when_close_in_space_and_time() -> None:
    pred = [
        PredPoint(
            dataset_key="x",
            species="tuna",
            lat=33.0,
            lon=-119.0,
            when=datetime(2008, 6, 1, 12, 0, tzinfo=timezone.utc),
        )
    ]
    prey = [
        PreyEvent(
            source="swfsc_cps_trawl_haul_catch",
            species="sardine",
            lat=33.01,
            lon=-119.01,
            when=datetime(2008, 6, 2, 12, 0, tzinfo=timezone.utc),
            event_id="t:2",
        )
    ]
    out = spatiotemporal_overlap(pred, prey)
    assert out["n_pred_matched"] == 1
    assert out["n_prey_matched"] == 1
