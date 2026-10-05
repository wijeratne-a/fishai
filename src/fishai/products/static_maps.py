"""Publish static egg-encounter maps. Doctrine is mandatory."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from fishai.products.surface_contract import validate_prediction_rows

DOCTRINE_PATH = Path(__file__).resolve().parents[3] / "configs" / "products" / "public_map_doctrine.yaml"
CELL_ID = re.compile(r"^g-?\d+_-?\d+$")
FORBIDDEN = re.compile(
    r"live fish|adult fish|fish tracking|tracking fish|harvest|where to fish|catch advice",
    re.IGNORECASE,
)


def load_doctrine(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load((path or DOCTRINE_PATH).read_text(encoding="utf-8"))


def apply_public_doctrine(rows: list[dict[str, Any]], doctrine: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return public rows. Out-of-domain and threatened taxa become UNKNOWN."""
    doctrine = doctrine or load_doctrine()
    validate_prediction_rows(rows)
    display = doctrine["display_evidence"]
    threatened = set(doctrine.get("threatened_species") or [])
    allowed = set(doctrine["allowed_public_species"])
    min_km = int(doctrine["min_resolution_km"])
    if min_km < 10:
        raise ValueError("public maps must be no finer than 10 km")
    published: list[dict[str, Any]] = []
    for row in rows:
        if "lon" in row or "lat" in row or "latitude" in row or "longitude" in row:
            raise ValueError("public maps must not carry point coordinates")
        res = row.get("resolution_km", min_km)
        if float(res) < 10:
            raise ValueError("public cell finer than 10 km")
        if not CELL_ID.match(str(row["cell_id"])):
            raise ValueError(f"cell_id {row['cell_id']} is not a 10 km block id")
        if row.get("layer") == "commercial_fishing_aggregate":
            n = int(row.get("n_vessels") or 0)
            if n < int(doctrine["min_vessels_commercial_aggregate"]):
                raise ValueError("commercial-fishing aggregates need 3 or more vessels")
        species = row["species"]
        if species not in allowed and species not in threatened:
            raise ValueError(f"species {species} is not cleared for a public map")
        out = dict(row)
        if species in threatened or int(row["ood_level"]) >= 2 or row["evidence_state"] == "UNKNOWN":
            reason = row.get("unknown_reason") or "ood_level_ge_2"
            if species in threatened:
                reason = "threatened_species_mask"
            out["evidence_state"] = "UNKNOWN"
            out["unknown_reason"] = reason
            out["p_encounter"] = None
            out["p_lo90"] = None
            out["p_hi90"] = None
            if int(out["ood_level"]) < 2 and species in threatened:
                out["ood_level"] = 2
        label = out.get("product_label") or ""
        if not re.search(r"\b(egg|spawning)\b", label, re.IGNORECASE):
            raise ValueError("user-facing product_label must say egg or spawning")
        if FORBIDDEN.search(label):
            raise ValueError("product_label implies tracking or harvest advice")
        state = out["evidence_state"]
        if state not in display:
            raise ValueError(f"no display evidence vocabulary for {state}")
        out["display_evidence"] = display[state]
        out["resolution_km"] = min_km
        out["life_stage_label"] = "egg / spawning habitat"
        published.append(out)
    validate_prediction_rows(published)
    return published


def render_static_map(rows: list[dict[str, Any]], doctrine: dict[str, Any] | None = None) -> str:
    doctrine = doctrine or load_doctrine()
    public = apply_public_doctrine(rows, doctrine)
    title = doctrine["user_facing_title"]
    lines = [
        "<!DOCTYPE html>",
        "<html lang=\"en\"><head><meta charset=\"utf-8\">",
        f"<title>{title}</title></head><body>",
        f"<h1>{title}</h1>",
        "<p>Egg-stage and spawning-habitat evidence only. "
        "Cells are 10 km blocks. Conditions outside the model domain are Unknown. "
        "This page does not give fishing advice.</p>",
        "<table>",
        "<thead><tr><th>Cell</th><th>Species</th><th>Valid day</th>"
        "<th>Evidence</th><th>Egg encounter probability</th></tr></thead>",
        "<tbody>",
    ]
    for row in public:
        if row["evidence_state"] == "UNKNOWN" or row["p_encounter"] is None:
            prob = "Unknown"
        else:
            prob = f"{float(row['p_encounter']):.2f}"
        ev = row["display_evidence"]
        lines.append(
            "<tr>"
            f"<td>{row['cell_id']}</td>"
            f"<td>{row['species']} egg</td>"
            f"<td>{row['valid_day']}</td>"
            f"<td>{ev}</td>"
            f"<td>{prob}</td>"
            "</tr>"
        )
    lines.append("</tbody></table></body></html>")
    html = "\n".join(lines)
    if FORBIDDEN.search(html):
        raise ValueError("rendered map contains a prohibited claim")
    if "egg" not in html.lower() or "spawning" not in html.lower():
        raise ValueError("rendered map must say egg and spawning")
    return html


def write_static_map(rows: list[dict[str, Any]], html_path: Path, json_path: Path) -> None:
    public = apply_public_doctrine(rows)
    html_path.write_text(render_static_map(public), encoding="utf-8")
    json_path.write_text(json.dumps(public, indent=2), encoding="utf-8")
