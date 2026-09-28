"""Synthetic CPS trawl haul-catch ingestion tests (no network)."""

from __future__ import annotations

import unittest
from pathlib import Path

from fishai.ingestion.biology.cps_trawl.catch import merge_catch_values, parse_catch_row
from fishai.ingestion.biology.cps_trawl.constants import ZERO_FRAME_STATUS_VERIFIED
from fishai.ingestion.biology.cps_trawl.fetch import read_cps_trawl_csv
from fishai.ingestion.biology.cps_trawl.matrix import ZeroFrameUnverifiedError, expand_haul_species_matrix
from fishai.ingestion.biology.cps_trawl.transform import (
    make_haul_id,
    tow_distance_nm,
    tow_duration_minutes,
    transform_rows,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


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
        # ~2 nm north at this latitude (short hop).
        dist = tow_distance_nm(33.0, -120.0, 33.03, -120.0)
        self.assertIsNotNone(dist)
        self.assertGreater(dist, 1.5)
        self.assertLess(dist, 2.5)


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
        self.assertIsNotNone(haul1["tow_distance_nm"])
        self.assertIsNone(haul1["net_mouth_area_m2"])
        self.assertEqual(haul1["net_mouth_area_m2_null_reason"], "not_in_source_dataset")

        sard = next(c for c in result.catch if c["species"] == "Sardinops sagax")
        self.assertEqual(sard["weight_kg"], 3.0)
        self.assertFalse(sard["presence_only"])

        po = next(c for c in result.catch if c["haul_id"].endswith(":2"))
        self.assertTrue(po["presence_only"])
        self.assertIsNone(po["weight_kg"])
        self.assertEqual(po["weight_null_reason"], "presence_only")


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
    def test_gate_blocks_implied_zeros(self) -> None:
        catch = [
            {
                "haul_id": "CPSTrawl:209901:SY:1",
                "species": "Sardinops sagax",
                "count": 1,
                "weight_kg": 1.0,
                "presence_only": False,
            }
        ]
        hauls = ["CPSTrawl:209901:SY:1"]
        species = ["Sardinops sagax", "Engraulis mordax"]
        with self.assertRaises(ZeroFrameUnverifiedError):
            expand_haul_species_matrix(catch, hauls, species, on_unverified="raise")

    def test_gate_na_mode(self) -> None:
        catch = [
            {
                "haul_id": "CPSTrawl:209901:SY:1",
                "species": "Sardinops sagax",
                "count": 1,
                "weight_kg": 1.0,
                "presence_only": False,
            }
        ]
        matrix = expand_haul_species_matrix(
            catch,
            ["CPSTrawl:209901:SY:1"],
            ["Sardinops sagax", "Engraulis mordax"],
            on_unverified="na",
        )
        anch = next(m for m in matrix if m["species"] == "Engraulis mordax")
        self.assertIsNone(anch["count"])
        self.assertEqual(anch["fill_reason"], "zero_frame_unverified")

    def test_verified_frame_emits_zeros(self) -> None:
        catch: list[dict] = []
        matrix = expand_haul_species_matrix(
            catch,
            ["CPSTrawl:209901:SY:1"],
            ["Sardinops sagax"],
            zero_frame_status=ZERO_FRAME_STATUS_VERIFIED,
        )
        self.assertEqual(matrix[0]["count"], 0)
        self.assertTrue(matrix[0]["is_implied_zero"])


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
        self.assertEqual(merged.count, 47)
        self.assertAlmostEqual(merged.weight_kg or 0, 0.7795)


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
