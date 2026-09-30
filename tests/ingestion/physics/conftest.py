"""Shared fixtures for physics ingestion tests."""

from __future__ import annotations

import datetime as dt
import re

import pytest

from fishai.ingestion.physics import wcofs_pds_s3_list
from fishai.ingestion.physics.sources import wcofs as wcofs_src
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


_DAY_PREFIX = re.compile(r"^wcofs/netcdf/(\d{4})/(\d{2})/(\d{2})/$")


def _offline_list_keys_under_prefix(prefix: str) -> list[str]:
    """Deterministic stand-in for the public PDS listing: every fields lead for the prefix day."""
    match = _DAY_PREFIX.match(prefix.lstrip("/"))
    if match is None:
        return []
    day = dt.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return [wcofs_src.fields_s3_key(day, lead) for lead in wcofs_src.ALL_FIELD_LEADS]


@pytest.fixture(autouse=True)
def _offline_wcofs_pds_listing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests never list the NOAA PDS bucket; tests inject ``list_keys`` to override."""
    monkeypatch.setattr(wcofs_pds_s3_list, "list_keys_under_prefix", _offline_list_keys_under_prefix)
