"""Pilot shoreline SHA for prereg gate tests (from overlap config path)."""

from __future__ import annotations

from fishai.scoring.harmonization.shoreline_gate import pilot_shoreline_sha256_from_overlap_config


def pilot_shoreline_sha_for_tests() -> str:
    return pilot_shoreline_sha256_from_overlap_config()
