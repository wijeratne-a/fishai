"""Synthetic CPS trawl haul-catch ingestion tests (no network)."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

import pyarrow.parquet as pq
import yaml

from fishai.ingestion.biology.cps_trawl.catch import (
    estimate_count_raised,
    merge_catch_values,
    parse_catch_row,
    resolve_weights,
)
from fishai.ingestion.biology.cps_trawl.constants import (
    ANIMALIA_ONLY_ZERO_FRAME_REASON,
    WEIGHT_FLAG_PARTIAL,
)
from fishai.ingestion.biology.cps_trawl.fetch import read_cps_trawl_csv
from fishai.ingestion.biology.cps_trawl.pipeline import sync_cps_trawl_haul_catch
from fishai.ingestion.biology.cps_trawl.matrix import ZeroFrameUnverifiedError, expand_haul_species_matrix
from fishai.ingestion.biology.cps_trawl.transform import (
    make_haul_id,
    tow_distance_nm,
    tow_duration_minutes,
    transform_rows,
)
from fishai.ingestion.biology.cps_trawl.zero_frame import (
    HAUL_NOT_IN_VERIFIED_FRAME_REASON,
    load_zero_frame_evidence,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
EVIDENCE_FIXTURE = FIXTURES / "cps_trawl_zero_frame_evidence_test.yaml"


class CpsTrawlHaulIdTests(unittest.TestCase):
    def test_stable_haul_id(self) -> None:
        self.assertEqual(make_haul_id("209901", "SY", 1), "CPSTrawl:209901:SY:1")


class CpsTrawlEffortTests(unittest.TestCase):
    def test_tow_duration_minutes(self) -> None:
        from datetime import datetime, timezone

        start = datetime(2099, 6, 1, 12, 0, tzinfo=timezone.utc)
        end = datetime(2099, 6, 1, 12, 30, tzinfo=timezone.utc)
        self.assertAlmostEqual(tow_duration_minutes(start, end), 30.0)

    def test_tow_distance_nm(self) -> None:
        dist = tow_distance_nm(33.0, -120.0, 33.03, -120.0)
        self.assertIsNotNone(dist)
        self.assertGreater(dist, 1.5)
        self.assertLess(dist, 2.5)


class CpsTrawlWeightPartialTests(unittest.TestCase):
    def test_single_weight_is_partial_not_total(self) -> None:
        parsed = parse_catch_row(
            {
                "scientific_name": "Engraulis mordax",
                "subsample_count": "47",
                "subsample_weight": "0.7795",
                "remaining_weight": "NaN",
                "presence_only": "N",
            }
        )
        assert parsed is not None
        self.assertIsNone(parsed.weight_kg)
        self.assertEqual(parsed.weight_flag, WEIGHT_FLAG_PARTIAL)
        self.assertAlmostEqual(parsed.subsample_weight_kg or 0, 0.7795)
        self.assertIsNone(parsed.remaining_weight_kg)
        self.assertIsNone(parsed.count_raised_est)
        self.assertEqual(parsed.count_raised_est_null_reason, "raising_weights_incomplete")

    def test_both_weights_sum_to_total(self) -> None:
        weight, flag, sub, rem = resolve_weights(1.0, 2.0)
        self.assertIsNone(flag)
        self.assertEqual(weight, 3.0)
        self.assertEqual(sub, 1.0)
        self.assertEqual(rem, 2.0)

    def test_count_raised_est_when_both_weights_valid(self) -> None:
        raised, reason = estimate_count_raised(10, 1.0, 2.0)
        self.assertIsNone(reason)
        self.assertEqual(raised, 30)


class CpsTrawlTransformFixtureTests(unittest.TestCase):
    def test_fixture_transform_hauls_and_catch(self) -> None:
        path = FIXTURES / "swfsc_cps_trawl_haul_catch_sample.csv"
        rows, skipped = read_cps_trawl_csv(path)
        result = transform_rows(rows, units_rows_skipped=skipped)
        self.assertEqual(result.qc_report["units_rows_skipped"], 1)
        self.assertEqual(len(result.hauls), 2)
        self.assertEqual(len(result.catch), 3)

        haul1 = next(h for h in result.hauls if h["haul"] == 1)
        self.assertAlmostEqual(haul1["tow_duration_min"], 30.0)
        self.assertFalse(haul1["animalia_only_haul"])

        sard = next(c for c in result.catch if c["species"] == "Sardinops sagax")
        self.assertEqual(sard["weight_kg"], 3.0)
        self.assertEqual(sard["subsample_count"], 10)
        self.assertEqual(sard["count_raised_est"], 30)
        self.assertFalse(sard["presence_only"])

        po = next(c for c in result.catch if c["haul_id"].endswith(":2"))
        self.assertTrue(po["presence_only"])
        self.assertIsNone(po["weight_kg"])


class CpsTrawlPresenceOnlyTests(unittest.TestCase):
    def test_presence_only_never_gets_weight(self) -> None:
        row = {
            "scientific_name": "Engraulis mordax",
            "subsample_count": "1",
            "subsample_weight": "5.0",
            "remaining_weight": "1.0",
            "presence_only": "Y",
        }
        parsed = parse_catch_row(row)
        assert parsed is not None
        self.assertIsNone(parsed.weight_kg)


class CpsTrawlZeroFrameGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.empty_evidence = FIXTURES / "cps_trawl_zero_frame_evidence_empty.yaml"
        cls.empty_evidence.write_text(
            yaml.dump({"version": 1, "cruise_frames": []}),
            encoding="utf-8",
        )

    def _catch_row(self) -> dict:
        return {
            "haul_id": "CPSTrawl:209901:SY:1",
            "species": "Sardinops sagax",
            "subsample_count": 1,
            "count_raised_est": None,
            "weight_kg": 1.0,
            "presence_only": False,
        }

    def test_gate_blocks_without_evidence_entry(self) -> None:
        with self.assertRaises(ZeroFrameUnverifiedError):
            expand_haul_species_matrix(
                [self._catch_row()],
                ["CPSTrawl:209901:SY:1"],
                ["Sardinops sagax", "Engraulis mordax"],
                evidence_path=self.empty_evidence,
                on_unverified="raise",
            )

    def test_unexplained_haul_number_blocked(self) -> None:
        with self.assertRaises(ZeroFrameUnverifiedError) as ctx:
            expand_haul_species_matrix(
                [],
                ["CPSTrawl:209901:SY:99"],
                ["Sardinops sagax"],
                evidence_path=EVIDENCE_FIXTURE,
                haul_meta=[{"haul_id": "CPSTrawl:209901:SY:99", "animalia_only_haul": False}],
                on_unverified="raise",
            )
        self.assertIn(HAUL_NOT_IN_VERIFIED_FRAME_REASON, str(ctx.exception))

    def test_verified_cruise_emits_zeros_for_listed_haul(self) -> None:
        matrix = expand_haul_species_matrix(
            [self._catch_row()],
            ["CPSTrawl:209901:SY:1"],
            ["Sardinops sagax", "Engraulis mordax"],
            evidence_path=EVIDENCE_FIXTURE,
            haul_meta=[{"haul_id": "CPSTrawl:209901:SY:1", "animalia_only_haul": False}],
        )
        anch = next(m for m in matrix if m["species"] == "Engraulis mordax")
        self.assertEqual(anch["subsample_count"], 0)
        self.assertTrue(anch["is_implied_zero"])

    def test_animalia_only_haul_never_gets_zeros(self) -> None:
        matrix = expand_haul_species_matrix(
            [{"haul_id": "CPSTrawl:209901:SY:1", "species": "Animalia", "subsample_count": None, "presence_only": False}],
            ["CPSTrawl:209901:SY:1"],
            ["Sardinops sagax"],
            evidence_path=EVIDENCE_FIXTURE,
            haul_meta=[{"haul_id": "CPSTrawl:209901:SY:1", "animalia_only_haul": True}],
            on_unverified="na",
        )
        cell = matrix[0]
        self.assertIsNone(cell["subsample_count"])
        self.assertEqual(cell["fill_reason"], ANIMALIA_ONLY_ZERO_FRAME_REASON)

    def test_evidence_mismatch_marks_cruise_invalid(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            yaml.dump(
                {
                    "version": 1,
                    "cruise_frames": [
                        {
                            "cruise": "209901",
                            "ship": "SY",
                            "source_report_citation": "bad",
                            "report_haul_log": [1, 2],
                            "aborted_tows": [],
                            "expected_hauls": [1],
                        }
                    ],
                },
                tmp,
            )
            bad_path = Path(tmp.name)
        evidence = load_zero_frame_evidence(bad_path)
        entry = evidence[("209901", "SY")]
        self.assertFalse(entry.valid)
        bad_path.unlink()


class CpsTrawlMergeSpeciesTests(unittest.TestCase):
    def test_weighted_row_wins_over_presence_only_duplicate(self) -> None:
        weighted = parse_catch_row(
            {
                "scientific_name": "Engraulis mordax",
                "subsample_count": "47",
                "subsample_weight": "0.7795",
                "remaining_weight": "NaN",
                "presence_only": "N",
            }
        )
        presence = parse_catch_row(
            {
                "scientific_name": "Engraulis mordax",
                "subsample_count": "NaN",
                "subsample_weight": "NaN",
                "remaining_weight": "NaN",
                "presence_only": "Y",
            }
        )
        assert weighted is not None and presence is not None
        merged = merge_catch_values([weighted, presence])
        self.assertFalse(merged.presence_only)
        self.assertEqual(merged.subsample_count, 47)
        self.assertIsNone(merged.weight_kg)
        self.assertEqual(merged.weight_flag, WEIGHT_FLAG_PARTIAL)

    def test_collection_split_missing_weights_stays_null_not_zero(self) -> None:
        """Regression: empty sum() used to pass 0+0 into resolve_weights → weight_kg=0.0."""
        split_a = parse_catch_row(
            {
                "scientific_name": "Sardinops sagax",
                "subsample_count": "5",
                "subsample_weight": "NaN",
                "remaining_weight": "NaN",
                "presence_only": "N",
            }
        )
        split_b = parse_catch_row(
            {
                "scientific_name": "Sardinops sagax",
                "subsample_count": "3",
                "subsample_weight": "NaN",
                "remaining_weight": "NaN",
                "presence_only": "N",
            }
        )
        assert split_a is not None and split_b is not None
        merged = merge_catch_values([split_a, split_b])
        self.assertEqual(merged.subsample_count, 8)
        self.assertIsNone(merged.weight_kg)
        self.assertFalse(merged.weight_present)
        self.assertEqual(merged.weight_null_reason, "weights_missing")

    def test_merge_mixed_missing_and_present_weight_stays_null(self) -> None:
        missing = parse_catch_row(
            {
                "scientific_name": "Sardinops sagax",
                "subsample_count": "5",
                "subsample_weight": "NaN",
                "remaining_weight": "NaN",
                "presence_only": "N",
            }
        )
        present = parse_catch_row(
            {
                "scientific_name": "Sardinops sagax",
                "subsample_count": "3",
                "subsample_weight": "1.0",
                "remaining_weight": "2.0",
                "presence_only": "N",
            }
        )
        assert missing is not None and present is not None
        merged = merge_catch_values([missing, present])
        self.assertIsNone(merged.weight_kg)
        self.assertFalse(merged.weight_present)
        self.assertEqual(merged.weight_null_reason, "weights_missing")


def _haul1_erddap_base() -> dict[str, str]:
    return {
        "cruise": "209901",
        "ship": "SY",
        "haul": "1",
        "latitude": "33.0",
        "longitude": "-120.0",
        "stop_latitude": "33.02",
        "stop_longitude": "-119.98",
        "time": "2099-06-01T12:00:00Z",
        "haulback_time": "2099-06-01T12:30:00Z",
        "presence_only": "N",
    }


def _sync_weight_semantics_fixture_rows() -> list[dict[str, str]]:
    """One haul: merged missing weights, single present total, genuine zero."""
    base = _haul1_erddap_base()
    return [
        {
            **base,
            "collection": "1",
            "scientific_name": "Sardinops sagax",
            "subsample_count": "5",
            "subsample_weight": "NaN",
            "remaining_weight": "NaN",
        },
        {
            **base,
            "collection": "2",
            "scientific_name": "Sardinops sagax",
            "subsample_count": "3",
            "subsample_weight": "NaN",
            "remaining_weight": "NaN",
        },
        {
            **base,
            "collection": "1",
            "scientific_name": "Engraulis mordax",
            "subsample_count": "10",
            "subsample_weight": "1.0",
            "remaining_weight": "2.0",
        },
        {
            **base,
            "collection": "1",
            "scientific_name": "Clupea pallasii",
            "subsample_count": "1",
            "subsample_weight": "0",
            "remaining_weight": "0",
        },
    ]


class CpsTrawlSyncMergeWeightTests(unittest.TestCase):
    def test_sync_merge_keeps_null_present_and_genuine_zero_weights(self) -> None:
        rows = _sync_weight_semantics_fixture_rows()
        with tempfile.TemporaryDirectory() as tmp:
            proc = Path(tmp) / "processed"
            with (
                mock.patch(
                    "fishai.ingestion.biology.cps_trawl.pipeline.processed_dir",
                    return_value=proc,
                ),
                mock.patch(
                    "fishai.ingestion.biology.cps_trawl.pipeline.load_raw_rows_for_window",
                ) as load_rows,
            ):
                load_rows.return_value = (rows, 0)
                result = sync_cps_trawl_haul_catch(
                    date(2099, 1, 1),
                    date(2099, 12, 31),
                    fetch=False,
                )
            records = pq.read_table(result["catch_path"]).to_pylist()
            by_species = {r["species"]: r for r in records}

        missing = by_species["Sardinops sagax"]
        self.assertIsNone(missing["weight_kg"])
        self.assertFalse(missing["weight_present"])
        self.assertEqual(missing["subsample_count"], 8)

        present = by_species["Engraulis mordax"]
        self.assertEqual(present["weight_kg"], 3.0)
        self.assertTrue(present["weight_present"])

        zero = by_species["Clupea pallasii"]
        self.assertEqual(zero["weight_kg"], 0.0)
        self.assertTrue(zero["weight_present"])


class CpsTrawlMissingWeightTests(unittest.TestCase):
    def test_missing_weight_not_zero(self) -> None:
        row = {
            "scientific_name": "Clupea",
            "subsample_count": "2",
            "subsample_weight": "NaN",
            "remaining_weight": "NaN",
            "presence_only": "N",
        }
        parsed = parse_catch_row(row)
        assert parsed is not None
        self.assertIsNone(parsed.weight_kg)
        self.assertNotEqual(parsed.weight_kg, 0.0)


if __name__ == "__main__":
    unittest.main()
