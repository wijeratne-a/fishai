"""Fail-closed behavior for Parquet and JSON coordinate scans."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "security"))

from precommit_sensitive_scan import (  # noqa: E402
    geojson_has_coordinate_geometry,
    scan_json_text,
    scan_parquet_file,
)


class ScanFailClosedTests(unittest.TestCase):
    def test_json_parse_error_is_hit(self) -> None:
        hits, fields = scan_json_text("{not json", rel="labels/bad.json")
        self.assertEqual(hits, ["json:parse_error"])
        self.assertEqual(fields, [])

    def test_parquet_unreadable_is_hit(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
            tmp.write(b"not-a-parquet-file")
            path = Path(tmp.name)
        try:
            hits, names = scan_parquet_file(path)
            self.assertEqual(hits, ["parquet:unreadable"])
            self.assertEqual(names, [])
        finally:
            path.unlink(missing_ok=True)

    def test_parquet_pyarrow_missing_is_hit(self) -> None:
        import precommit_sensitive_scan as scan_mod

        with patch.object(
            scan_mod,
            "_import_pyarrow_parquet",
            side_effect=ImportError("no pyarrow"),
        ):
            hits, names = scan_mod.scan_parquet_file(Path(__file__))
        self.assertEqual(hits, ["parquet:pyarrow_missing"])
        self.assertEqual(names, [])

    def test_geojson_multipoint_and_linestring_flagged(self) -> None:
        mp = {"type": "MultiPoint", "coordinates": [[1.0, 2.0], [3.0, 4.0]]}
        ls = {"type": "LineString", "coordinates": [[1.0, 2.0], [3.0, 4.0]]}
        self.assertTrue(geojson_has_coordinate_geometry(mp))
        self.assertTrue(geojson_has_coordinate_geometry(ls))
        hits_mp, _ = scan_json_text(__import__("json").dumps(mp), rel="x.geojson")
        hits_ls, _ = scan_json_text(__import__("json").dumps(ls), rel="x.geojson")
        self.assertIn("geojson:coordinate_geometry", hits_mp)
        self.assertIn("geojson:coordinate_geometry", hits_ls)


if __name__ == "__main__":
    unittest.main()
