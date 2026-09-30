"""Pinned GLORYS catalogue env for R subprocess tests (no live Copernicus)."""

from __future__ import annotations

import datetime as dt
import subprocess
import sys
from pathlib import Path

import pytest

from fishai.ingestion.physics.glorys_catalog import (
    GlorysCatalogError,
    clear_glorys_catalog_cache,
    load_catalog_entries,
    resolve_glorys_dataset_for_date,
    set_catalog_fetch_hook,
)
from fishai.ingestion.physics.sources.glorys import PRODUCT_ID_MY, glorys_product_for_date

REPO = Path(__file__).resolve().parents[3]
PINNED = REPO / "src" / "models" / "tests" / "fixtures" / "glorys_pinned_catalog.json"
CLI = REPO / "scripts" / "ci" / "glorys_product_for_date_cli.py"


def test_pinned_catalog_env_resolves_without_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FISHAI_GLORYS_PINNED_CATALOG_JSON", str(PINNED))
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(None)
    assert glorys_product_for_date(dt.date(2020, 6, 1)) == PRODUCT_ID_MY
    resolution = resolve_glorys_dataset_for_date(dt.date(2020, 6, 1))
    assert resolution.dataset_id == PRODUCT_ID_MY


def test_glorys_cli_subprocess_uses_pinned_catalog_env() -> None:
    import os

    full_env = os.environ.copy()
    full_env["FISHAI_GLORYS_PINNED_CATALOG_JSON"] = str(PINNED)
    proc = subprocess.run(
        [sys.executable, str(CLI), "2020-06-01"],
        check=True,
        capture_output=True,
        text=True,
        env=full_env,
        cwd=str(REPO),
    )
    assert proc.stdout.strip() == PRODUCT_ID_MY


def test_live_catalog_unreachable_raises_when_unpinned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FISHAI_GLORYS_PINNED_CATALOG_JSON", raising=False)
    clear_glorys_catalog_cache()
    set_catalog_fetch_hook(None)

    def _boom() -> list:
        raise GlorysCatalogError("catalog_unreachable", "glorys: Copernicus Marine catalogue unreachable (test)")

    monkeypatch.setattr(
        "fishai.ingestion.physics.glorys_catalog._fetch_catalog_entries_live",
        lambda: _boom(),
    )
    with pytest.raises(GlorysCatalogError) as exc:
        load_catalog_entries()
    assert exc.value.reason_code == "catalog_unreachable"
