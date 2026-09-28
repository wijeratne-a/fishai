"""Coordinate exposure checks for committed artifacts (shared by CI scanners)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

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

SENSITIVE_GEOMETRY_TYPES = frozenset(
    {"Point", "MultiPoint", "LineString", "MultiLineString"},
)


def field_name_exposes_coordinates(name: str) -> bool:
    normalized = name.replace(" ", "_").lower()
    if normalized in COORD_HEADER_NAMES:
        return True
    snake = re.sub(r"([a-z])([A-Z])", r"\1_\2", name).replace(" ", "_").lower()
    return snake in COORD_HEADER_NAMES


def header_has_coordinates(fields: list[str]) -> bool:
    return any(field_name_exposes_coordinates(field) for field in fields)


def csv_header_fields(first_line: str) -> list[str]:
    return [h.strip().strip('"').strip("'").lower() for h in first_line.strip().split(",")]


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


def _geometry_exposes_coordinates(geom: Mapping[str, Any]) -> bool:
    gtype = geom.get("type")
    if gtype not in SENSITIVE_GEOMETRY_TYPES:
        return False
    coords = geom.get("coordinates")
    if not isinstance(coords, list) or not coords:
        return False
    if gtype == "Point":
        return len(coords) >= 2
    if gtype == "LineString":
        return isinstance(coords[0], (list, tuple)) and len(coords) >= 2
    if gtype == "MultiPoint":
        return isinstance(coords[0], (list, tuple))
    if gtype == "MultiLineString":
        return isinstance(coords[0], list) and coords[0]
    return False


def geojson_has_coordinate_geometry(node: object) -> bool:
    """True when GeoJSON contains Point, MultiPoint, LineString, or MultiLineString coordinates."""
    if not isinstance(node, dict):
        return False
    gtype = node.get("type")
    if gtype == "Feature":
        geom = node.get("geometry")
        return geojson_has_coordinate_geometry(geom) if isinstance(geom, dict) else False
    if gtype == "FeatureCollection":
        features = node.get("features")
        if isinstance(features, list):
            return any(geojson_has_coordinate_geometry(f) for f in features)
    if isinstance(node.get("geometry"), dict) and geojson_has_coordinate_geometry(node["geometry"]):
        return True
    if gtype in SENSITIVE_GEOMETRY_TYPES and _geometry_exposes_coordinates(node):
        return True
    return False


def scan_json_content(text: str, *, rel: str = "") -> list[str]:
    """
    Scan JSON/GeoJSON text for coordinate schema names or coordinate geometries.

    Fail closed: invalid JSON is reported as ``json_parse:invalid``.
    """
    hits: list[str] = []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return ["json_parse:invalid"]
    schema_contract = rel.startswith("src/fishai/schemas/") or rel.endswith(".schema.json")
    if not schema_contract:
        for name in walk_json_property_names(data):
            if field_name_exposes_coordinates(name):
                hits.append("json_schema:latitude_or_longitude")
                break
    if geojson_has_coordinate_geometry(data):
        hits.append("geojson:coordinate_geometry")
    return hits


def parquet_schema_field_names(path: Path) -> list[str]:
    """Return Parquet column names, or [] when the schema cannot be read."""
    try:
        import pyarrow.parquet as pq
    except ImportError:
        return []
    try:
        return list(pq.read_schema(path).names)
    except Exception:
        return []


def scan_parquet_path(path: Path) -> list[str]:
    """
    Scan a Parquet file schema for coordinate column names.

    Fail closed: missing pyarrow or unreadable files are reported as hits.
    """
    try:
        import pyarrow.parquet as pq
    except ImportError:
        return ["parquet_scan:pyarrow_missing"]
    try:
        schema = pq.read_schema(path)
    except Exception:
        return ["parquet_scan:unreadable"]
    hits: list[str] = []
    for name in schema.names:
        if field_name_exposes_coordinates(name):
            hits.append("parquet_schema:latitude_or_longitude")
    return hits


# Backward-compatible alias used in early tests.
geojson_has_point_geometry = geojson_has_coordinate_geometry
