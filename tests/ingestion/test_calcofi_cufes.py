"""Synthetic CUFES ingestion tests (no network, no real survey coordinates)."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from fishai.ingestion.biology.cufes import BBox, build_erddap_csv_url, sync_cufes
from fishai.ingestion.biology.cufes.constants import (
    EGG_CATEGORIES,
    QC_COUNT_INVALID,
    QC_DURATION_OUT_OF_RANGE,
    QC_KEY_INVALID,
)
from fishai.ingestion.biology.cufes.transform import parse_egg_count
from fishai.ingestion.biology.cufes.transform import (
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
        vol, pumps_used = volume_m3_for_row(row)
        self.assertIsNotNone(vol)
        self.assertEqual(pumps_used, 2)
        # mean pump 0.5 m³/min × 30 min = 15 m³
        self.assertAlmostEqual(vol, 15.0, places=5)

    def test_single_pump_reading_when_stop_missing(self) -> None:
        row = _synthetic_row(stop_pump="")
        row["stop_pump_speed"] = ""
        vol, pumps_used = volume_m3_for_row(row)
        self.assertEqual(pumps_used, 1)
        self.assertIsNotNone(vol)
        result = transform_rows([row])
        self.assertEqual(result.events[0]["pump_readings_used"], 1)

    def test_parse_egg_count_accepts_whole_float_text(self) -> None:
        self.assertEqual(parse_egg_count("3.0"), 3)


class CufesPumpQcTests(unittest.TestCase):
    def test_stop_pump_40_drops_under_pump_invalid(self) -> None:
        row = _synthetic_row(stop_pump="40.0")
        result = transform_rows([row])
        self.assertEqual(result.events, [])
        self.assertEqual(result.qc_report["dropped_by_rule"]["pump_invalid"], 1)
        self.assertEqual(result.qc_report["pump_qc_detail"]["pump_out_of_bounds"], 1)

    def test_pump_ratio_above_two_drops(self) -> None:
        row = _synthetic_row(start_pump="0.564", stop_pump="0.270")
        result = transform_rows([row])
        self.assertEqual(result.events, [])
        self.assertEqual(result.qc_report["dropped_by_rule"]["pump_invalid"], 1)
        self.assertEqual(result.qc_report["pump_qc_detail"]["pump_ratio"], 1)

    def test_pump_below_min_drops(self) -> None:
        row = _synthetic_row(start_pump="0.12", stop_pump="0.8")
        result = transform_rows([row])
        self.assertEqual(result.events, [])
        self.assertEqual(result.qc_report["pump_qc_detail"]["pump_out_of_bounds"], 1)

    def test_valid_pump_pair_kept(self) -> None:
        row = _synthetic_row(start_pump="0.8", stop_pump="0.9")
        result = transform_rows([row])
        self.assertEqual(len(result.events), 1)
        self.assertEqual(result.events[0]["pump_readings_used"], 2)


class CufesInvalidCountTests(unittest.TestCase):
    def test_invalid_sardine_eggs_drop_whole_event(self) -> None:
        for sardine in ("", "abc", "-1", "2.5"):
            with self.subTest(sardine=sardine):
                row = _synthetic_row(sardine=sardine, anchovy="5")
                result = transform_rows([row])
                self.assertEqual(result.events, [])
                self.assertEqual(result.counts, [])
                self.assertTrue(qc_flags_for_row(row) & QC_COUNT_INVALID)
                self.assertGreater(result.qc_report["dropped_by_rule"]["count_invalid"], 0)


class CufesKeyTests(unittest.TestCase):
    def test_blank_ship_code_dropped(self) -> None:
        row = _synthetic_row(ship_code="   ")
        self.assertTrue(qc_flags_for_row(row) & QC_KEY_INVALID)
        result = transform_rows([row])
        self.assertEqual(result.events, [])
        self.assertEqual(result.qc_report["dropped_by_rule"]["key_invalid"], 1)

    def test_duplicate_event_id_raises(self) -> None:
        row = _synthetic_row(sample_number="7")
        with self.assertRaises(ValueError) as ctx:
            transform_rows([row, row])
        self.assertIn("CUFES:209901:99:7", str(ctx.exception))


class CufesQcTests(unittest.TestCase):
    def test_drops_reversed_time(self) -> None:
        row = _synthetic_row(stop_time="2099-06-01T11:00:00Z")
        result = transform_rows([row])
        self.assertEqual(result.events, [])
        self.assertEqual(result.counts, [])
        self.assertNotEqual(qc_flags_for_row(row), 0)

    def test_drops_impossible_latitude(self) -> None:
        row = _synthetic_row(lat="125.0")
        self.assertNotEqual(qc_flags_for_row(row), 0)
        result = transform_rows([row])
        self.assertEqual(result.events, [])

    def test_duration_qc_drops_all_species_rows_including_zeros(self) -> None:
        # 120 min duration exceeds default max (90 min); sardine count > 0 must not leak zeros.
        row = _synthetic_row(
            sardine="42",
            stop_time="2099-06-01T14:00:00Z",
        )
        self.assertTrue(qc_flags_for_row(row) & QC_DURATION_OUT_OF_RANGE)
        result = transform_rows([row])
        self.assertEqual(result.events, [])
        self.assertEqual(result.counts, [])
        self.assertEqual(result.qc_report["dropped_by_rule"]["duration_out_of_range"], 1)
        self.assertEqual(result.qc_report["events_kept"], 0)


class CufesOccurrenceTests(unittest.TestCase):
    def test_six_categories_with_explicit_zeros(self) -> None:
        row = _synthetic_row()
        result = transform_rows([row])
        self.assertEqual(len(result.events), 1)
        self.assertEqual(len(result.counts), 6)
        taxa = {c["taxon"] for c in result.counts}
        self.assertEqual(taxa, {t[1] for t in EGG_CATEGORIES})
        sardine = next(c for c in result.counts if c["taxon"] == "sardine")
        self.assertEqual(sardine["count"], 0)
        self.assertEqual(sardine["occurrence_status"], "absent")
        anchovy = next(c for c in result.counts if c["taxon"] == "anchovy")
        self.assertEqual(anchovy["count"], 2)
        self.assertEqual(anchovy["occurrence_status"], "present")


class CufesEventsContractTests(unittest.TestCase):
    def test_event_id_unique_and_required_fields(self) -> None:
        rows = [
            _synthetic_row(sample_number="1"),
            _synthetic_row(sample_number="2", ship_code="98"),
        ]
        result = transform_rows(rows)
        ids = [ev["event_id"] for ev in result.events]
        self.assertEqual(len(ids), len(set(ids)))
        for ev in result.events:
            for key in (
                "event_id",
                "time",
                "lat",
                "lon",
                "stop_time",
                "stop_lat",
                "stop_lon",
                "volume_m3",
                "pump_readings_used",
            ):
                self.assertIsNotNone(ev[key])
            self.assertIn(ev["pump_readings_used"], (1, 2))
            self.assertEqual(ev["qc_flags"], 0)
        count_event_ids = {c["event_id"] for c in result.counts}
        self.assertEqual(count_event_ids, set(ids))


class CufesQcReportTests(unittest.TestCase):
    def test_qc_report_counts_add_up(self) -> None:
        good = _synthetic_row(sample_number="1")
        bad = _synthetic_row(sample_number="2", lat="200.0")
        result = transform_rows([good, bad])
        report = result.qc_report
        self.assertEqual(report["events_read"], 2)
        self.assertEqual(report["events_kept"], 1)
        self.assertEqual(report["dropped_unique_total"], 1)
        self.assertEqual(report["events_read"], report["events_kept"] + report["dropped_rows"])


class CufesUrlEncodingTests(unittest.TestCase):
    def test_constraints_are_percent_encoded(self) -> None:
        from datetime import datetime, timezone

        url = build_erddap_csv_url(
            datetime(2099, 1, 1, tzinfo=timezone.utc),
            datetime(2099, 2, 1, tzinfo=timezone.utc),
            BBox(10.0, 11.0, -11.0, -10.0),
            fields=("time", "latitude"),
        )
        self.assertIn("time%3E=", url)
        self.assertIn("time%3C", url)
        self.assertIn("latitude%3E=", url)
        self.assertIn("latitude%3C=", url)
        self.assertNotIn("time>=", url)


class CufesSyncTests(unittest.TestCase):
    def test_sync_no_fetch_writes_parquet_and_qc_report(self) -> None:
        row = _synthetic_row()
        with tempfile.TemporaryDirectory() as tmp:
            proc = Path(tmp) / "processed"
            with (
                mock.patch("fishai.ingestion.biology.cufes.pipeline.processed_dir", return_value=proc),
                mock.patch("fishai.ingestion.biology.cufes.pipeline.load_raw_rows_for_window") as load_rows,
            ):
                load_rows.return_value = [row]
                result = sync_cufes(date(2099, 1, 1), date(2099, 12, 31), fetch=False)
            self.assertEqual(result["n_events"], 1)
            self.assertTrue(Path(result["events_path"]).is_file())
            self.assertTrue(Path(result["counts_path"]).is_file())
            qc_path = Path(result["qc_report_path"])
            self.assertTrue(qc_path.is_file())
            report = json.loads(qc_path.read_text(encoding="utf-8"))
            self.assertEqual(report["events_kept"], 1)


if __name__ == "__main__":
    unittest.main()
