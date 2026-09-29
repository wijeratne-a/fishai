"""Instrument coordinate exemption (record_type: instrument in SOURCES.yaml)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "security"))

from instrument_coordinate_policy import (  # noqa: E402
    apply_instrument_coordinate_exemption,
    instrument_source_ids,
    parquet_fishai_source_id,
    resolve_source_id,
)
from precommit_sensitive_scan import scan_file  # noqa: E402


class InstrumentCoordinateExceptionTests(unittest.TestCase):
    def test_manifest_lists_approved_enabled_instrument_sources_only(self) -> None:
        ids = instrument_source_ids()
        self.assertEqual(ids, frozenset({"sccoos_hfr", "ndbc_met", "spray_glider"}))

    def test_glider_pending_disabled_not_exempt(self) -> None:
        rel = "tests/fixtures/instrument_data/ioos_glider_dac/_tmp_glider.parquet"
        full = REPO / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        table = pa.table({"lat": [33.0], "lon": [-120.0], "temperature": [18.0], "depth": [10.0]})
        meta = {b"fishai_source_id": b"ioos_glider_dac"}
        pq.write_table(table.replace_schema_metadata(meta), full)
        try:
            hits = scan_file(rel)
            self.assertIn("parquet_schema:latitude_or_longitude", hits)
        finally:
            full.unlink(missing_ok=True)

    def test_tracked_ndbc_fixture_csv_with_lat_lon_passes_scan(self) -> None:
        rel = "tests/fixtures/instrument_data/ndbc_met/public_instrument_sample.csv"
        hits = scan_file(rel)
        coord_hits = [h for h in hits if "latitude_or_longitude" in h or "coordinate_geometry" in h]
        self.assertEqual(coord_hits, [])

    def test_tracked_hfr_fixture_csv_with_lat_lon_passes_scan(self) -> None:
        rel = "tests/fixtures/instrument_data/sccoos_hfr/public_instrument_sample.csv"
        hits = scan_file(rel)
        coord_hits = [h for h in hits if "latitude_or_longitude" in h or "coordinate_geometry" in h]
        self.assertEqual(coord_hits, [])

    def test_tagged_parquet_outside_instrument_folder_not_exempt(self) -> None:
        rel = "tests/fixtures/ndbc_tagged_outside_instrument.parquet"
        full = REPO / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        table = pa.table({"lat": [33.0], "lon": [-120.0], "WTMP": [18.0]})
        pq.write_table(
            table.replace_schema_metadata({b"fishai_source_id": b"ndbc_met"}),
            full,
        )
        try:
            self.assertIsNone(resolve_source_id(rel, path=full))
            hits = scan_file(rel)
            self.assertIn("parquet_schema:latitude_or_longitude", hits)
        finally:
            full.unlink(missing_ok=True)

    def test_parquet_in_folder_with_mismatched_tag_not_exempt(self) -> None:
        rel = "tests/fixtures/instrument_data/ndbc_met/_tmp_mismatched_tag.parquet"
        full = REPO / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        table = pa.table({"lat": [33.0], "lon": [-120.0], "WTMP": [18.0]})
        pq.write_table(
            table.replace_schema_metadata({b"fishai_source_id": b"sccoos_hfr"}),
            full,
        )
        try:
            self.assertIsNone(resolve_source_id(rel, path=full))
            hits = scan_file(rel)
            self.assertIn("parquet_schema:latitude_or_longitude", hits)
        finally:
            full.unlink(missing_ok=True)

    def test_disallowed_column_individual_count_revokes_exemption(self) -> None:
        self._assert_disallowed_column_revokes("station,lat,lon,individualCount\n1,33.0,-120.0,5\n")

    def test_disallowed_column_scientific_name_revokes_exemption(self) -> None:
        self._assert_disallowed_column_revokes("station,lat,lon,scientificName\n1,33.0,-120.0,Sardinops\n")

    def test_disallowed_column_sardine_eggs_revokes_exemption(self) -> None:
        self._assert_disallowed_column_revokes("station,lat,lon,sardine_eggs\n1,33.0,-120.0,12\n")

    def _assert_disallowed_column_revokes(self, body: str) -> None:
        rel = "tests/fixtures/instrument_data/ndbc_met/_tmp_bad_cols.csv"
        full = REPO / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(body, encoding="utf-8")
        try:
            hits = scan_file(rel)
            self.assertTrue(
                any(h.startswith("instrument:disallowed_column:") for h in hits)
                or any("csv_header:latitude_or_longitude" in h for h in hits)
            )
        finally:
            full.unlink(missing_ok=True)

    def test_parquet_lat_lon_exempt_under_instrument_path(self) -> None:
        rel = "tests/fixtures/instrument_data/ndbc_met/_tmp_scan.parquet"
        full = REPO / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        table = pa.table({"lat": [33.0], "lon": [-120.0], "WTMP": [18.0]})
        pq.write_table(
            table.replace_schema_metadata({b"fishai_source_id": b"ndbc_met"}),
            full,
        )
        try:
            hits = scan_file(rel)
            self.assertNotIn("parquet_schema:latitude_or_longitude", hits)
        finally:
            full.unlink(missing_ok=True)

    def test_untagged_parquet_in_folder_resolves_to_folder_source(self) -> None:
        rel = "tests/fixtures/instrument_data/ndbc_met/_tmp_untagged_resolve.parquet"
        full = REPO / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        table = pa.table({"lat": [33.0], "lon": [-120.0], "WTMP": [18.0]})
        pq.write_table(table, full)
        try:
            self.assertIsNone(parquet_fishai_source_id(full))
            self.assertEqual(resolve_source_id(rel, path=full), "ndbc_met")
        finally:
            full.unlink(missing_ok=True)

    def test_untagged_parquet_allowlisted_columns_exempt_under_instrument_path(self) -> None:
        rel = "tests/fixtures/instrument_data/ndbc_met/_tmp_untagged_allowlisted.parquet"
        full = REPO / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        table = pa.table(
            {
                "station": ["46086"],
                "time": ["2024-01-01T00:00:00Z"],
                "lat": [33.0],
                "lon": [-120.0],
                "depth": [0.0],
                "WTMP": [18.0],
            }
        )
        pq.write_table(table, full)
        try:
            hits = scan_file(rel)
            self.assertNotIn("parquet_schema:latitude_or_longitude", hits)
            self.assertFalse(any(h.startswith("instrument:disallowed_column:") for h in hits))
        finally:
            full.unlink(missing_ok=True)

    def test_untagged_parquet_disallowed_column_revokes_exemption(self) -> None:
        rel = "tests/fixtures/instrument_data/ndbc_met/_tmp_untagged_bad_cols.parquet"
        full = REPO / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        table = pa.table(
            {
                "station": ["46086"],
                "lat": [33.0],
                "lon": [-120.0],
                "individualCount": [5],
            }
        )
        pq.write_table(table, full)
        try:
            hits = scan_file(rel)
            self.assertIn("parquet_schema:latitude_or_longitude", hits)
            self.assertTrue(any(h.startswith("instrument:disallowed_column:ndbc_met:") for h in hits))
        finally:
            full.unlink(missing_ok=True)

    def test_apply_exemption_unit_allowlisted_columns(self) -> None:
        hits = ["parquet_schema:latitude_or_longitude"]
        out = apply_instrument_coordinate_exemption(
            "tests/fixtures/instrument_data/ndbc_met/x.parquet",
            hits,
            ["lat", "lon", "WTMP"],
        )
        self.assertEqual(out, [])

    def test_apply_exemption_unit_disallowed_column(self) -> None:
        hits = ["parquet_schema:latitude_or_longitude"]
        out = apply_instrument_coordinate_exemption(
            "tests/fixtures/instrument_data/ndbc_met/x.parquet",
            hits,
            ["lat", "lon", "species"],
        )
        self.assertTrue(any("disallowed_column" in h for h in out))


if __name__ == "__main__":
    unittest.main()
