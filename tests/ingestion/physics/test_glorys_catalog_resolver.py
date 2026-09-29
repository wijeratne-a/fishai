"""Live-catalogue GLORYS dataset resolution (mocked; no network in CI)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest
import requests

from fishai.ingestion.physics.glorys_catalog import (
    FIXTURE_ENV,
    GLORYS_CANDIDATE_DATASET_IDS,
    GLORYS_DATASET_ID,
    GlorysCatalogEntry,
    GlorysCatalogError,
    clear_glorys_catalog_cache,
    resolve_glorys_dataset_for_date,
    set_catalog_fetch_hook,
)
from fishai.ingestion.physics.sources.glorys import PRODUCT_ID_MY, glorys_product_for_date

DEPRECATED_MYINT_PRODUCT_ID = "cmems_mod_glo_phy_myint_0.083deg_P1D-m"


def _entries(*items: GlorysCatalogEntry) -> list[GlorysCatalogEntry]:
    return list(items)


def test_only_my_is_catalog_candidate() -> None:
    assert GLORYS_CANDIDATE_DATASET_IDS == (GLORYS_DATASET_ID,)
    assert DEPRECATED_MYINT_PRODUCT_ID not in GLORYS_CANDIDATE_DATASET_IDS


def test_resolve_never_returns_myint_product_id() -> None:
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(
        lambda: _entries(
            GlorysCatalogEntry(
                dataset_id=PRODUCT_ID_MY,
                dataset_version="202311",
                coverage_start=dt.date(1993, 1, 1),
                coverage_end=dt.date(2026, 6, 23),
            )
        )
    )
    for day in (
        dt.date(1998, 3, 15),
        dt.date(2021, 7, 1),
        dt.date(2024, 9, 1),
        dt.date(2025, 9, 1),
    ):
        resolved = glorys_product_for_date(day)
        assert resolved == PRODUCT_ID_MY
        assert resolved != DEPRECATED_MYINT_PRODUCT_ID


def test_2024_date_resolves_to_my() -> None:
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(
        lambda: _entries(
            GlorysCatalogEntry(
                dataset_id=PRODUCT_ID_MY,
                dataset_version="202311",
                coverage_start=dt.date(1993, 1, 1),
                coverage_end=dt.date(2026, 6, 23),
            )
        )
    )
    resolution = resolve_glorys_dataset_for_date(dt.date(2024, 9, 1))
    assert resolution.dataset_id == PRODUCT_ID_MY
    assert resolution.dataset_version == "202311"
    assert resolution.catalog_coverage["end"] == "2026-06-23"
    assert glorys_product_for_date(dt.date(2024, 9, 1)) == PRODUCT_ID_MY


def test_date_outside_coverage_returns_reason_code() -> None:
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(
        lambda: _entries(
            GlorysCatalogEntry(
                dataset_id=PRODUCT_ID_MY,
                dataset_version="202311",
                coverage_start=dt.date(1993, 1, 1),
                coverage_end=dt.date(2020, 12, 31),
            )
        )
    )
    with pytest.raises(GlorysCatalogError) as exc:
        resolve_glorys_dataset_for_date(dt.date(2024, 9, 1))
    assert exc.value.reason_code == "glorys_date_not_covered"


def test_catalog_failure_returns_reason_code() -> None:
    clear_glorys_catalog_cache()

    def _boom() -> list[GlorysCatalogEntry]:
        raise GlorysCatalogError("catalog_unreachable", "simulated outage")

    set_catalog_fetch_hook(_boom)
    with pytest.raises(GlorysCatalogError) as exc:
        resolve_glorys_dataset_for_date(dt.date(2020, 1, 1))
    assert exc.value.reason_code == "catalog_unreachable"


def _refuse_network(*_args: object, **_kwargs: object) -> None:
    raise requests.ConnectionError("Remote end closed connection without response")


def test_live_catalogue_connection_error_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(FIXTURE_ENV, raising=False)
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(None)
    monkeypatch.setattr(requests.Session, "get", _refuse_network)
    with pytest.raises(GlorysCatalogError) as exc:
        resolve_glorys_dataset_for_date(dt.date(2020, 6, 1))
    assert exc.value.reason_code == "catalog_unreachable"


def test_fixture_env_does_not_call_the_network(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "models"
        / "tests"
        / "fixtures"
        / "glorys_catalog_fixture.json"
    )
    monkeypatch.setenv(FIXTURE_ENV, str(fixture))
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(None)
    monkeypatch.setattr(requests.Session, "get", _refuse_network)
    resolved = resolve_glorys_dataset_for_date(dt.date(2020, 6, 1))
    assert resolved.dataset_id == PRODUCT_ID_MY
    assert resolved.dataset_version == "202311"


def test_missing_fixture_file_is_fail_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(FIXTURE_ENV, str(tmp_path / "missing-catalog.json"))
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(None)
    monkeypatch.setattr(requests.Session, "get", _refuse_network)
    with pytest.raises(GlorysCatalogError) as exc:
        resolve_glorys_dataset_for_date(dt.date(2020, 6, 1))
    assert exc.value.reason_code == "catalog_unreachable"


def test_missing_candidates_raise_not_in_catalog() -> None:
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(lambda: [])
    with pytest.raises(GlorysCatalogError) as exc:
        resolve_glorys_dataset_for_date(dt.date(2020, 1, 1))
    assert exc.value.reason_code == "glorys_dataset_not_in_catalog"
