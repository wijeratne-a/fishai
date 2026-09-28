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
)
from precommit_sensitive_scan import scan_file  # noqa: E402


class InstrumentCoordinateExceptionTests(unittest.TestCase):
    def test_manifest_lists_three_instrument_sources(self) -> None:
        ids = instrument_source_ids()
        self.assertEqual(ids, frozenset({"sccoos_hfr", "ndbc_met", "ioos_glider_dac"}))

    def test_tracked_fixture_csv_with_lat_lon_passes_scan(self) -> None:
        rel = "tests/fixtures/instrument_data/ndbc_met/public_instrument_sample.csv"
        hits = scan_file(rel)
        coord_hits = [h for h in hits if "latitude_or_longitude" in h or "coordinate_geometry" in h]
        self.assertEqual(coord_hits, [])

    def test_instrument_exemption_revoked_when_species_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text("station,lat,lon,species\n1,33.0,-120.0,sardine\n", encoding="utf-8")
            rel = "tests/fixtures/instrument_data/ndbc_met/bad_species.csv"
            full = REPO / rel
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            try:
                hits = scan_file(rel)
                self.assertTrue(
                    any(h.startswith("instrument:fishery_field_with_coordinates") for h in hits)
                    or any("csv_header:latitude_or_longitude" in h for h in hits)
                )
            finally:
                full.unlink(missing_ok=True)

    def test_parquet_lat_lon_exempt_under_instrument_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rel = "tests/fixtures/instrument_data/ndbc_met/_tmp_scan.parquet"
            full = REPO / rel
            full.parent.mkdir(parents=True, exist_ok=True)
            table = pa.table({"lat": [33.0], "lon": [-120.0], "WTMP": [18.0]})
            pq.write_table(table, full)
            try:
                hits = scan_file(rel)
                self.assertNotIn("parquet_schema:latitude_or_longitude", hits)
            finally:
                full.unlink(missing_ok=True)

    def test_apply_exemption_unit(self) -> None:
        hits = ["parquet_schema:latitude_or_longitude"]
        out = apply_instrument_coordinate_exemption(
            "tests/fixtures/instrument_data/ndbc_met/x.parquet",
            hits,
            ["lat", "lon", "WTMP"],
        )
        self.assertEqual(out, [])
        out_bad = apply_instrument_coordinate_exemption(
            "tests/fixtures/instrument_data/ndbc_met/x.parquet",
            hits,
            ["lat", "lon", "species"],
        )
        self.assertTrue(any("fishery_field" in h for h in out_bad))


if __name__ == "__main__":
    unittest.main()
