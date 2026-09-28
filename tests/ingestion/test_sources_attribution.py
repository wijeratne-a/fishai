"""SOURCES.yaml attribution contract."""

from __future__ import annotations

import yaml

from fishai.ingestion.sources import MANIFEST_PATH, load_sources_manifest


def test_every_enabled_source_has_nonempty_attribution() -> None:
    data = load_sources_manifest()
    sources = data.get("sources") or {}
    missing = [
        source_id
        for source_id, entry in sources.items()
        if isinstance(entry, dict)
        and entry.get("enabled") is True
        and not str(entry.get("attribution") or "").strip()
    ]
    assert not missing, f"enabled sources without attribution: {missing}"


def test_glorys_attribution_exact_string() -> None:
    entry = load_sources_manifest()["sources"]["glorys"]
    expected = (
        "Generated using E.U. Copernicus Marine Service Information; "
        "https://doi.org/10.48670/moi-00021"
    )
    assert entry["attribution"] == expected


def test_manifest_parses() -> None:
    yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
