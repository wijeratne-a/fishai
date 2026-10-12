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


def test_ood_level_at_least_2_is_unknown() -> None:
    payload = load_fixture()
    ood = [r for r in payload["rows"] if r["ood_level"] >= 2]
    assert len(ood) >= 1
    for row in ood:
        assert row["evidence_state"] == "UNKNOWN"
        assert row["p_encounter"] is None
        assert row["unknown_reason"]


def test_public_resolution_floor() -> None:
    payload = load_fixture()
    assert payload["meta"]["public_resolution_floor_km"] >= 10
    assert payload["meta"]["cell_spacing_km"] >= 10
    readme = (PROTOTYPE_DIR / "README.md").read_text(encoding="utf-8")
    assert "10 km" in readme
    app = (PROTOTYPE_DIR / "app.js").read_text(encoding="utf-8")
    assert "finer than 10 km" in app
    assert "ood_level" in app or "isUnknownRow" in app


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

    for path in ui_sources:
        for snippet in _user_visible_strings(path):
            snippet = snippet.strip()
            if not snippet:
                continue
            if snippet in ("Anchovy", "Sardine"):
                continue
            if "${" in snippet and not EGG_OR_SPAWNING.search(snippet):
                continue
            assert EGG_OR_SPAWNING.search(snippet), (
                f"user-facing text missing egg/spawning in {path.name}: {snippet!r}"
            )
        text = path.read_text(encoding="utf-8")
        for label in re.findall(r"<strong>([^<]+)</strong>", text):
            label = label.strip()
            if not label:
                continue
            assert EGG_OR_SPAWNING.search(label), (
                f"field label missing egg/spawning in {path.name}: {label!r}"
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
    assert "no egg dots in this 10 km patch" in app_js
    assert "if (!unknown && row.p_encounter != null)" in app_js
    assert "effectiveEvidenceState" in app_js
    display = (PROTOTYPE_DIR / "evidence_display.js").read_text(encoding="utf-8")
    assert "ood_level" in display


def test_day_control_and_summary_present() -> None:
    html = (PROTOTYPE_DIR / "index.html").read_text(encoding="utf-8")
    app_js = (PROTOTYPE_DIR / "app.js").read_text(encoding="utf-8")
    assert 'data-testid="day-select"' in html or "day-select" in app_js
    assert "summary-headline" in html
    assert "computeSummaryHeadline" in app_js
    assert "renderDayControl" in app_js
    payload = load_fixture()
    days = payload["meta"].get("demo_days") or sorted({r["valid_day"] for r in payload["rows"]})
    assert len(days) >= 3
