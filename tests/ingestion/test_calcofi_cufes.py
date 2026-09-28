"""Synthetic CUFES ingestion tests (no network, no real survey coordinates)."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from fishai.ingestion.biology.cufes_constants import EGG_CATEGORIES
from fishai.ingestion.biology.cufes_fetch import BBox, build_erddap_csv_url
from fishai.ingestion.biology.cufes_pipeline import sync_cufes
from fishai.ingestion.biology.cufes_transform import (
    make_event_id,
    qc_flags_for_row,
    transform_rows,
    volume_m3_for_row,
)


def _synthetic_row(
    *,
    cruise: str = "209901",
    ship_code: str = "99",
    sample_number: str = "1",
    start_time: str = "2099-06-01T12:00:00Z",
    stop_time: str = "2099-06-01T12:30:00Z",
    lat: str = "10.0",
    lon: str = "-10.0",
    stop_lat: str = "10.01",
    stop_lon: str = "-10.01",
    start_pump: str = "0.5",
    stop_pump: str = "0.7",
    sardine: str = "0",
    anchovy: str = "2",
) -> dict[str, str]:
    return {
        "cruise": cruise,
        "ship": "SYNTH",
        "ship_code": ship_code,
        "sample_number": sample_number,
        "time": start_time,
        "latitude": lat,
        "longitude": lon,
        "start_pump_speed": start_pump,
        "stop_time": stop_time,
        "stop_latitude": stop_lat,
        "stop_longitude": stop_lon,
        "stop_pump_speed": stop_pump,
        "sardine_eggs": sardine,
        "anchovy_eggs": anchovy,
        "jack_mackerel_eggs": "0",
        "hake_eggs": "0",
        "squid_eggs": "0",
        "other_fish_eggs": "0",
    }


class CufesEventIdTests(unittest.TestCase):
    def test_ship_code_required_for_uniqueness(self) -> None:
        a = make_event_id("209901", "01", 12)
        b = make_event_id("209901", "02", 12)
        self.assertNotEqual(a, b)
        self.assertEqual(a, "CUFES:209901:01:12")


class CufesEffortTests(unittest.TestCase):
    def test_volume_m3_from_pump_and_duration(self) -> None:
        row = _synthetic_row(start_pump="0.4", stop_pump="0.6")
        vol = volume_m3_for_row(row)
        self.assertIsNotNone(vol)
        # mean pump 0.5 m³/min × 30 min = 15 m³
        self.assertAlmostEqual(vol, 15.0, places=5)


class CufesQcTests(unittest.TestCase):
    def test_drops_reversed_time(self) -> None:
        row = _synthetic_row(stop_time="2099-06-01T11:00:00Z")
        events, counts = transform_rows([row])
        self.assertEqual(events, [])
        self.assertEqual(counts, [])
        self.assertNotEqual(qc_flags_for_row(row), 0)

    def test_drops_impossible_latitude(self) -> None:
        row = _synthetic_row(lat="125.0")
        self.assertNotEqual(qc_flags_for_row(row), 0)
        events, _ = transform_rows([row])
        self.assertEqual(events, [])


class CufesOccurrenceTests(unittest.TestCase):
    def test_six_categories_with_explicit_zeros(self) -> None:
        row = _synthetic_row()
        events, counts = transform_rows([row])
        self.assertEqual(len(events), 1)
        self.assertEqual(len(counts), 6)
        taxa = {c["taxon"] for c in counts}
        self.assertEqual(taxa, {t[1] for t in EGG_CATEGORIES})
        sardine = next(c for c in counts if c["taxon"] == "sardine")
        self.assertEqual(sardine["count"], 0)
        self.assertEqual(sardine["occurrence_status"], "absent")
        anchovy = next(c for c in counts if c["taxon"] == "anchovy")
        self.assertEqual(anchovy["count"], 2)
        self.assertEqual(anchovy["occurrence_status"], "present")


class CufesUrlEncodingTests(unittest.TestCase):
    def test_constraints_are_percent_encoded(self) -> None:
        from datetime import datetime, timezone

        url = build_erddap_csv_url(
            datetime(2099, 1, 1, tzinfo=timezone.utc),
            datetime(2099, 2, 1, tzinfo=timezone.utc),
            BBox(10.0, 11.0, -11.0, -10.0),
            fields=("time", "latitude"),
        )
        self.assertIn("time%3E%3D", url)
        self.assertIn("time%3C", url)
        self.assertIn("latitude%3E%3D", url)
        self.assertNotIn("time>=", url)


class CufesSyncTests(unittest.TestCase):
    def test_sync_no_fetch_writes_parquet(self) -> None:
        row = _synthetic_row()
        header = ",".join(row.keys())
        csv_body = header + "\n" + ",".join(row.values()) + "\n"
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw"
            raw.mkdir()
            (raw / "erdCalCOFIcufes_2099.csv").write_text(csv_body, encoding="utf-8")
            proc = Path(tmp) / "processed"
            with (
                mock.patch("fishai.ingestion.biology.cufes_pipeline.processed_dir", return_value=proc),
                mock.patch("fishai.ingestion.biology.cufes_pipeline.load_raw_rows_for_window") as load_rows,
            ):
                load_rows.return_value = [row]
                result = sync_cufes(date(2099, 1, 1), date(2099, 12, 31), fetch=False)
            self.assertEqual(result["n_events"], 1)
            self.assertTrue(Path(result["events_path"]).is_file())
            self.assertTrue(Path(result["counts_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
