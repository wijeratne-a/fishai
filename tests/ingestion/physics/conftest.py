"""Shared fixtures for physics ingestion tests."""

from __future__ import annotations

import datetime as dt

import pytest

from fishai.ingestion.physics.glorys_catalog import (
    GlorysCatalogEntry,
    clear_glorys_catalog_cache,
    set_catalog_fetch_hook,
)

_DEFAULT_MY = GlorysCatalogEntry(
    dataset_id="cmems_mod_glo_phy_my_0.083deg_P1D-m",
    dataset_version="202311",
    coverage_start=dt.date(1993, 1, 1),
    coverage_end=dt.date(2026, 6, 23),
)


@pytest.fixture(autouse=True)
def _mock_glorys_catalog() -> None:
    """CI has no Copernicus catalogue access; use a stable mock unless overridden."""

    def _hook() -> list[GlorysCatalogEntry]:
        return [_DEFAULT_MY]

    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(_hook)
    yield
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(None)
