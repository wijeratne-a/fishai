#!/usr/bin/env python3
"""Scan git-tracked files for credentials and coordinate exposure.

Uses ``git ls-files``. Skips gitignored runtime trees under ``data/processed/``, etc.

Instrument sources declared with ``record_type: instrument`` in ``data/SOURCES.yaml``
may expose public instrument lat/lon in tracked fixture paths (see
``instrument_coordinate_policy.INSTRUMENT_PATH_PREFIXES``) unless fishery-dependent
fields (species, count, catch*) appear in the same file.

Parquet and JSON/GeoJSON scans fail closed: unreadable or unparseable inputs are hits.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from instrument_coordinate_policy import apply_instrument_coordinate_exemption

REPO_ROOT = Path(__file__).resolve().parents[1]

SKIP_PREFIXES = (
    "data/raw/",
    "data/interim/",
    "data/restricted/",
    "data/quarantine/",
    "data/processed/",
)

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".csv",
    ".tsv",
    ".json",
    ".geojson",
    ".yaml",
    ".yml",
    ".env",
    ".toml",
    ".ini",
    ".cfg",
    ".sh",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".sql",
    ".xml",
}

CREDENTIAL_PATTERNS = [
    ("aws_access_key_id", re.compile(r"(?i)\bAKIA[0-9A-Z]{16}\b")),
    ("pem_private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    (
        "generic_api_key_assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[=:]\s*['\"][^'\"]{12,}['\"]"
        ),
    ),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9\-_\.]{20,}")),
    ("password_assignment", re.compile(r"(?i)\bpassword\s*[=:]\s*['\"][^'\"]{6,}['\"]")),
]

COORD_HEADER_NAMES = {
    "latitude",
    "longitude",
    "lat",
    "lon",
    "lng",
    "decimal_latitude",
    "decimal_longitude",
    "decimallatitude",
    "decimallongitude",
    "lat_dd",
    "lon_dd",
    "start_latitude",
    "start_longitude",
    "stop_latitude",
    "stop_longitude",
}


def git_ls_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=REPO_ROOT, text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]


def should_skip(rel: str) -> bool:
    return any(rel == p.rstrip("/") or rel.startswith(p) for p in SKIP_PREFIXES)


def read_text_limited(path: Path, max_bytes: int = 2_000_000) -> str | None:
    try:
        data = path.read_bytes()[:max_bytes]
    except OSError:
        return None
    if b"\x00" in data[:4096]:
        return None
    return data.decode("utf-8", errors="replace")


def csv_header_fields(first_line: str) -> list[str]:
    return [h.strip().strip('"').strip("'") for h in first_line.strip().split(",")]


def field_name_exposes_coordinates(name: str) -> bool:
    normalized = name.replace(" ", "_").lower()
    if normalized in COORD_HEADER_NAMES:
        return True
    snake = re.sub(r"([a-z])([A-Z])", r"\1_\2", name).replace(" ", "_").lower()
    return snake in COORD_HEADER_NAMES


def header_has_coordinates(fields: list[str]) -> bool:
    return any(field_name_exposes_coordinates(field) for field in fields)


def walk_json_property_names(node: object) -> list[str]:
    names: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            names.append(str(key))
            names.extend(walk_json_property_names(value))
    elif isinstance(node, list):
        for item in node:
            names.extend(walk_json_property_names(item))
    return names


def _coords_look_like_positions(coords: object) -> bool:
    if not isinstance(coords, list) or len(coords) < 2:
        return False
    if isinstance(coords[0], (int, float)):
        return True
    if isinstance(coords[0], list) and len(coords[0]) >= 2:
        return isinstance(coords[0][0], (int, float))
    return False


def geojson_has_coordinate_geometry(node: object) -> bool:
    """True for GeoJSON Point, MultiPoint, or LineString geometries."""
    if not isinstance(node, dict):
        return False
    gtype = node.get("type")
    if gtype in {"Point", "MultiPoint", "LineString"}:
        return _coords_look_like_positions(node.get("coordinates"))
    if gtype == "Feature":
        geom = node.get("geometry")
        return geojson_has_coordinate_geometry(geom) if isinstance(geom, dict) else False
    if gtype == "FeatureCollection":
        features = node.get("features")
        if isinstance(features, list):
            return any(geojson_has_coordinate_geometry(f) for f in features)
    geometry = node.get("geometry")
    if isinstance(geometry, dict) and geojson_has_coordinate_geometry(geometry):
        return True
    return False


def geojson_has_point_geometry(node: object) -> bool:
    """Backward-compatible alias (Point/MultiPoint/LineString)."""
    return geojson_has_coordinate_geometry(node)


def scan_json_text(text: str, *, rel: str = "") -> tuple[list[str], list[str]]:
    hits: list[str] = []
    field_names: list[str] = []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return ["json:parse_error"], field_names
    field_names = walk_json_property_names(data)
    schema_contract = rel.startswith("src/fishai/schemas/") or rel.endswith(".schema.json")
    if not schema_contract:
        for name in field_names:
            if field_name_exposes_coordinates(name):
                hits.append("json_schema:latitude_or_longitude")
                break
    if geojson_has_coordinate_geometry(data):
        hits.append("geojson:coordinate_geometry")
    return hits, field_names


def _import_pyarrow_parquet():
    import pyarrow.parquet as pq

    return pq


def scan_parquet_file(path: Path) -> tuple[list[str], list[str]]:
    try:
        pq = _import_pyarrow_parquet()
    except ImportError:
        return ["parquet:pyarrow_missing"], []
    try:
        schema = pq.read_schema(path)
    except Exception:
        return ["parquet:unreadable"], []
    names = list(schema.names)
    hits: list[str] = []
    for name in names:
        if field_name_exposes_coordinates(name):
            hits.append("parquet_schema:latitude_or_longitude")
    return hits, names


def scan_file(rel: str) -> list[str]:
    """Return hit kind strings for a tracked relative path."""
    if should_skip(rel):
        return []
    path = REPO_ROOT / rel
    if not path.is_file():
        return []

    suffix = path.suffix.lower()
    credential_hits: list[str] = []
    hits: list[str] = []
    field_names: list[str] = []

    if suffix == ".parquet":
        hits, field_names = scan_parquet_file(path)
    else:
        if suffix not in TEXT_SUFFIXES and path.name not in {".env", "Makefile"}:
            return []
        text = read_text_limited(path)
        if text is None:
            return []
        for kind, pattern in CREDENTIAL_PATTERNS:
            if pattern.search(text):
                credential_hits.append(f"credential:{kind}")
        if suffix in {".csv", ".tsv"}:
            first = text.splitlines()[0] if text else ""
            delim_fields = csv_header_fields(first.replace("\t", ","))
            field_names = delim_fields
            if header_has_coordinates(delim_fields):
                hits.append("csv_header:latitude_or_longitude")
        if suffix in {".json", ".geojson"} or rel.endswith(".schema.json"):
            json_hits, json_fields = scan_json_text(text, rel=rel)
            hits.extend(json_hits)
            field_names.extend(json_fields)

    non_exempt = [h for h in hits if h.startswith(("parquet:", "json:"))]
    exemptable = [h for h in hits if h not in non_exempt]
    exemptable = apply_instrument_coordinate_exemption(rel, exemptable, field_names, path=path)
    return credential_hits + non_exempt + exemptable


def scan_repository() -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for rel in git_ls_files():
        for kind in scan_file(rel):
            findings.append((kind, rel))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default="",
        help="Optional single file (repo-relative). Default: all git ls-files.",
    )
    args = parser.parse_args(argv)

    if args.path:
        rel = args.path.lstrip("/")
        hits = [(k, rel) for k in scan_file(rel)]
    else:
        hits = scan_repository()

    for kind, rel in hits:
        print(f"HIT\t{kind}\t{rel}")

    if hits:
        print(f"RESULT\tFAIL\thits={len(hits)}", file=sys.stderr)
        return 1

    print("RESULT\tPASS\thits=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
