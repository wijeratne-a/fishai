"""Spray glider ingest (fixture only in CI)."""

from __future__ import annotations

from fishai.ingestion.sensors.spray_glider import load_spray_glider_profiles


def test_load_spray_fixture_parquet() -> None:
    df = load_spray_glider_profiles()
    assert {"depth", "temperature", "mission", "profile"}.issubset(df.columns)
    assert len(df) > 0
