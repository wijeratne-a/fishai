"""Tests for extended coordinate exposure checks (JSON / GeoJSON / Parquet)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "security"))

from coordinate_exposure import (  # noqa: E402
    field_name_exposes_coordinates,
    geojson_has_coordinate_geometry,
    scan_json_content,
    scan_parquet_path,
)


class CoordinateScanExtensionTests(unittest.TestCase):
    def test_json_property_latitude_flagged_outside_schema_contracts(self) -> None:
        payload = {"event_id": "x", "latitude": 1.0, "longitude": 2.0}
        hits = scan_json_content(json.dumps(payload), rel="labels/example.json")
        self.assertIn("json_schema:latitude_or_longitude", hits)

    def test_schema_contract_path_skips_property_names(self) -> None:
        payload = {"properties": {"latitude": {"type": "number"}}}
        hits = scan_json_content(json.dumps(payload), rel="src/fishai/schemas/event.schema.json")
        self.assertNotIn("json_schema:latitude_or_longitude", hits)

    def test_geojson_point_geometry_flagged(self) -> None:
        payload = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [1.0, 2.0]},
            "properties": {},
        }
        self.assertTrue(geojson_has_coordinate_geometry(payload))
        hits = scan_json_content(json.dumps(payload), rel="data/manifests/x.geojson")
        self.assertIn("geojson:coordinate_geometry", hits)

    def test_geojson_linestring_geometry_flagged(self) -> None:
        payload = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [[1.0, 2.0], [3.0, 4.0]]},
            "properties": {},
        }
        self.assertTrue(geojson_has_coordinate_geometry(payload))
        hits = scan_json_content(json.dumps(payload), rel="x.geojson")
        self.assertIn("geojson:coordinate_geometry", hits)

    def test_parquet_schema_latitude_column(self) -> None:
        import pyarrow as pa
        import pyarrow.parquet as pq

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.parquet"
            table = pa.table({"latitude": [1.0], "event_id": ["a"]})
            pq.write_table(table, path)
            hits = scan_parquet_path(path)
            self.assertIn("parquet_schema:latitude_or_longitude", hits)

    def test_parquet_scan_fail_closed_without_pyarrow(self) -> None:
        import builtins

        import coordinate_exposure as ce

        original_import = builtins.__import__

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "pyarrow.parquet":
                raise ImportError("no pyarrow")
            return original_import(name, globals, locals, fromlist, level)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.parquet"
            path.write_bytes(b"PAR1")
            with mock.patch("builtins.__import__", side_effect=guarded_import):
                hits = ce.scan_parquet_path(path)
            self.assertEqual(hits, ["parquet_scan:pyarrow_missing"])

    def test_json_parse_fail_closed(self) -> None:
        hits = scan_json_content("{not json", rel="labels/bad.json")
        self.assertEqual(hits, ["json_parse:invalid"])

    def test_parquet_unreadable_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.parquet"
            path.write_bytes(b"not-parquet")
            hits = scan_parquet_path(path)
            self.assertIn("parquet_scan:unreadable", hits)

    def test_start_latitude_field_name(self) -> None:
        self.assertTrue(field_name_exposes_coordinates("start_latitude"))


if __name__ == "__main__":
    unittest.main()
