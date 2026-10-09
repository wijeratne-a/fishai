"""Public egg-encounter map doctrine."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fishai.products.static_maps import apply_public_doctrine, load_doctrine, render_static_map

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "hindcast_surface_rows.json"


def test_map_uses_display_vocabulary_and_egg_wording() -> None:
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    html = render_static_map(rows)
    for label in ("Historical Pattern", "Unknown", "egg", "spawning"):
        assert label.lower() in html.lower() or label in html
    assert "harvest" not in html.lower()
    assert "adult" not in html.lower()
    public = apply_public_doctrine(rows)
    unknown = [r for r in public if r["cell_id"] == "g10_21"][0]
    assert unknown["evidence_state"] == "UNKNOWN"
    assert unknown["p_encounter"] is None
    assert unknown["display_evidence"] == "Unknown"


def test_threatened_species_masks_probability() -> None:
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    doctrine = load_doctrine()
    doctrine["threatened_species"] = ["sardine"]
    doctrine["allowed_public_species"] = ["sardine", "anchovy"]
    public = apply_public_doctrine(rows, doctrine)
    sardine = [r for r in public if r["species"] == "sardine"][0]
    assert sardine["evidence_state"] == "UNKNOWN"
    assert sardine["unknown_reason"] == "threatened_species_mask"
    assert sardine["p_encounter"] is None
    assert sardine["display_evidence"] == "Unknown"


def test_fine_grid_and_few_vessels_fail() -> None:
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fine = dict(rows[0])
    fine["resolution_km"] = 1
    with pytest.raises(ValueError, match="10 km"):
        apply_public_doctrine([fine])
    vessels = dict(rows[0])
    vessels["layer"] = "commercial_fishing_aggregate"
    vessels["n_vessels"] = 2
    with pytest.raises(ValueError, match="3"):
        apply_public_doctrine([vessels])


def test_point_coordinates_rejected() -> None:
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    bad = dict(rows[0])
    bad["lon"] = -119.0
    with pytest.raises(ValueError, match="coordinates"):
        apply_public_doctrine([bad])
