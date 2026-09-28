#!/usr/bin/env python3
"""Unit tests for coordinate-header exposure screening."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from precommit_sensitive_scan import header_has_coordinates, csv_header_fields, scan_file


class CoordinateExposureTest(unittest.TestCase):
    def test_public_header_without_lat_lon_passes(self) -> None:
        fields = csv_header_fields("source_id,year,scientific_name,num_detected")
        self.assertFalse(header_has_coordinates(fields))

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "public.csv"
            path.write_text("source_id,year,scientific_name,num_detected\na,2020,X,1\n", encoding="utf-8")
            # Place under a fake audit-like relative path by scanning absolute; scan_file
            # uses REPO_ROOT-relative policy. Call header helper path directly above;
            # also ensure scan_file on a temp file outside protected zones reports header hit only when present.
            hits = scan_file(path, Path(tmp))
            kinds = [k for k, _ in hits]
            self.assertNotIn("csv_header:latitude_or_longitude", kinds)

    def test_header_with_latitude_fails(self) -> None:
        fields = csv_header_fields("event_id,latitude,longitude,scientific_name")
        self.assertTrue(header_has_coordinates(fields))

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "exposed.csv"
            path.write_text("event_id,latitude,longitude,scientific_name\n", encoding="utf-8")
            hits = scan_file(path, Path(tmp))
            kinds = [k for k, _ in hits]
            self.assertIn("csv_header:latitude_or_longitude", kinds)


if __name__ == "__main__":
    unittest.main()
