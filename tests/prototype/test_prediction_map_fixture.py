"""Hermetic checks for prediction-map synthetic fixture and UX copy."""

from __future__ import annotations

import json
import re
from pathlib import Path

import jsonschema
import pytest

REPO = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO / "configs" / "schemas" / "cufes_prediction_output.schema.json"
FIXTURE_PATH = REPO / "prototype" / "prediction-map" / "fixtures" / "synthetic_cufes_grid.json"
PROTOTYPE_DIR = REPO / "prototype" / "prediction-map"

SCHEMA_STATES = {
    "HINDCAST_GLORYS",
    "NOWCAST_UNVALIDATED",
    "FORECAST",
    "DEGRADED",
    "UNKNOWN",
}

DISPLAY_DOCTRINE = [
    "Direct Observation",
    "Historical Pattern",
    "Current Nowcast",
    "Forecast",
    "Unknown",
]

FORBIDDEN_UI_PHRASES = (
    "live fish",
    "fish location",
    "adult presence",
    "fish tracking",
    "tracking fish",
)

EGG_OR_SPAWNING = re.compile(r"\b(egg|spawning)\b", re.IGNORECASE)


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_fixture_rows_validate_against_schema() -> None:
    schema = load_schema()
    payload = load_fixture()
    rows = payload["rows"]
    assert len(rows) >= 1
    for row in rows:
        jsonschema.validate(row, schema)


def test_fixture_dry_run_and_species_coverage() -> None:
    payload = load_fixture()
    rows = payload["rows"]
    assert all(row["dry_run"] is True for row in rows)
    species = {row["species"] for row in rows}
    assert species == {"sardine", "anchovy"}
    states = {row["evidence_state"] for row in rows}
    assert states == SCHEMA_STATES


def test_unknown_rows_have_reason_and_null_probability() -> None:
    payload = load_fixture()
    unknown_rows = [r for r in payload["rows"] if r["evidence_state"] == "UNKNOWN"]
    assert len(unknown_rows) >= 1
    for row in unknown_rows:
        assert row["unknown_reason"]
        assert row["p_encounter"] is None


def test_watermark_declares_synthetic_fixture() -> None:
    payload = load_fixture()
    wm = payload["meta"]["watermark"].lower()
    assert "synthetic" in wm
    assert "fixture" in wm
    assert "nowcast" in wm


def _user_visible_strings(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".html":
        return re.findall(r">([^<>]{4,})<", text)
    if path.name == "app.js":
        return [
            s
            for s in re.findall(r"`([^`]{8,})`", text)
            if re.search(r"[A-Za-z]{3,}.* ", s) or "<" in s
        ]
    return []


def test_prototype_ui_labels_use_egg_or_spawning_and_avoid_fish_tracking_copy() -> None:
    ui_sources = [
        PROTOTYPE_DIR / "index.html",
        PROTOTYPE_DIR / "app.js",
        PROTOTYPE_DIR / "README.md",
    ]
    combined = "\n".join(p.read_text(encoding="utf-8") for p in ui_sources).lower()
    for phrase in FORBIDDEN_UI_PHRASES:
        assert phrase not in combined, f"forbidden phrase: {phrase}"

    doctrine_or_schema = re.compile(
        r"schema|evidence_state|display doctrine|direct observation|historical pattern|"
        r"current nowcast|forecast|unknown|hindcast_glorys|nowcast_unvalidated|degraded",
        re.IGNORECASE,
    )
    for path in ui_sources:
        for snippet in _user_visible_strings(path):
            snippet = snippet.strip()
            if not snippet:
                continue
            if doctrine_or_schema.search(snippet):
                continue
            assert EGG_OR_SPAWNING.search(snippet), (
                f"user-facing text missing egg/spawning in {path.name}: {snippet!r}"
            )

    watermark = load_fixture()["meta"]["watermark"]
    assert "synthetic" in watermark.lower() and "fixture" in watermark.lower()
    assert EGG_OR_SPAWNING.search(watermark)


def test_display_doctrine_list_matches_readme_vocabulary() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    for label in DISPLAY_DOCTRINE:
        assert label in text
    js = (PROTOTYPE_DIR / "evidence_display.js").read_text(encoding="utf-8")
    for label in DISPLAY_DOCTRINE:
        assert label in js


def test_schema_enum_visible_in_ui() -> None:
    js = (PROTOTYPE_DIR / "app.js").read_text(encoding="utf-8")
    for state in SCHEMA_STATES:
        assert state in js or state in (PROTOTYPE_DIR / "evidence_display.js").read_text(
            encoding="utf-8"
        )


def test_unknown_not_drawn_as_probability() -> None:
    app_js = (PROTOTYPE_DIR / "app.js").read_text(encoding="utf-8")
    assert "isUnknownRow" in app_js
    assert "No egg-encounter probability (UNKNOWN)" in app_js
    assert "if (!unknown && row.p_encounter != null)" in app_js
