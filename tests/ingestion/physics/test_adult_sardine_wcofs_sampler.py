"""Issued-forecast key resolution for the adult sardine 24h sampler. No network."""

from __future__ import annotations

import datetime as dt
import importlib.util
from pathlib import Path

import pytest

from fishai.ingestion.physics.wcofs_pds_store import CycleNotAvailable

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "scripts" / "models" / "sample_adult_sardine_24h_wcofs_covariates.py"


def _load_sampler():
    spec = importlib.util.spec_from_file_location("sardine_wcofs_sampler", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_fields_key_preferred_over_regulargrid():
    sampler = _load_sampler()
    day = dt.date(2024, 7, 29)
    keys = [
        "wcofs/netcdf/202407/nos.wcofs.fields.f024.20240729.t03z.nc",
        "wcofs/netcdf/202407/wcofs.t03z.20240729.regulargrid.f024.nc",
    ]

    def list_keys(prefix: str):
        return [key for key in keys if key.startswith(prefix)]

    resolved = sampler._resolve_issued_key(day, "f024", list_keys)
    assert resolved.endswith("nos.wcofs.fields.f024.20240729.t03z.nc")


def test_regulargrid_key_when_fields_forecast_is_absent():
    sampler = _load_sampler()
    day = dt.date(2026, 6, 25)
    keys = [
        "wcofs/netcdf/2026/06/25/wcofs.t03z.20260625.fields.n024.nc",
        "wcofs/netcdf/2026/06/25/wcofs.t03z.20260625.regulargrid.f024.nc",
    ]

    def list_keys(prefix: str):
        return [key for key in keys if key.startswith(prefix)]

    resolved = sampler._resolve_issued_key(day, "f024", list_keys)
    assert resolved.endswith("regulargrid.f024.nc")


def test_missing_forecast_lead_raises():
    sampler = _load_sampler()
    day = dt.date(2026, 6, 25)

    def list_keys(prefix: str):
        key = "wcofs/netcdf/2026/06/25/wcofs.t03z.20260625.fields.n024.nc"
        return [key] if key.startswith(prefix) else []

    with pytest.raises(CycleNotAvailable):
        sampler._resolve_issued_key(day, "f024", list_keys)
