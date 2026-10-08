"""Synthetic CPS nearshore set-catch ingestion tests (no network)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from fishai.ingestion.biology.cps_nearshore.catch import (
    catch_row_invalid,
    parse_catch_row,
)
from fishai.ingestion.biology.cps_nearshore.constants import (
    ITIS_TSN_ENGRAULIS_MORDAX,
    ITIS_TSN_SARDINOPS_SAGAX,
    PILOT_SPECIES_ITIS_TSN,
    SOURCE_ID,
)
from fishai.ingestion.biology.cps_nearshore import pipeline as nearshore_pipeline
from fishai.ingestion.biology.cps_nearshore.fetch import (
    build_erddap_csv_url,
    read_cps_nearshore_csv,
)
from fishai.ingestion.biology.cps_nearshore.matrix import (
    ZeroFrameUnverifiedError,
    expand_set_species_matrix,
)
from fishai.ingestion.biology.cps_nearshore.transform import (
    make_set_id,
    transform_rows,
)
from fishai.ingestion.biology.cps_nearshore.zero_frame import (
    SET_NOT_IN_VERIFIED_FRAME_REASON,
    load_zero_frame_evidence,
    set_zero_frame_status,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
EVIDENCE_FIXTURE = FIXTURES / "cps_nearshore_zero_frame_evidence_test.yaml"


def _evidence_yaml_tmp(tmpdir: Path, *, sets: list[int] = [1]) -> Path:
    path = tmpdir / "evidence.yaml"
    path.write_text(
        yaml.dump(
            {
                "version": 1,
                "cruise_frames": [
                    {
                        "cruise": "209901",
                        "ship": "SY",
                        "source_report_citation": "Temp-dir e2e fixture.",
                        "report_set_log": sets,
                        "aborted_sets": [],
                        "expected_sets": sets,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def _catch_row(set_no: int, name: str, tsn: int | None, n: int | None, kg: float | None) -> dict:
    return {
        "cruise": "209901",
        "ship": "SY",
        "date": "2099-07-01",
        "time_PDT": "12:00",
        "time": "2099-07-01T19:00:00Z",
        "set": str(set_no),
        "latitude": "34.0",
        "longitude": "-120.0",
        "state": "CA",
        "gearType": "purse seine",
        "itis_tsn": "" if tsn is None else str(tsn),
        "scientific_name": name,
        "totalNumber": "" if n is None else str(n),
        "totalWeightkg": "" if kg is None else str(kg),
    }


class NearshoreIngestionTests(unittest.TestCase):
    def test_source_id(self) -> None:
        self.assertEqual(SOURCE_ID, "swfsc_cps_nearshore_set_catch")

    def test_stable_set_id(self) -> None:
        self.assertEqual(make_set_id("209901", "SY", 3), "CPSNearshore:209901:SY:3")

    def test_erddap_url_targets_nearshore_dataset(self) -> None:
        from datetime import datetime, timezone

        url = build_erddap_csv_url(
            datetime(2024, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        self.assertIn("FRDCPSNearshoreSetCatch.csv?", url)
        self.assertIn("time%3E=", url)

    def test_parse_catch_row_totals(self) -> None:
        parsed = parse_catch_row(
            _catch_row(1, "Sardinops sagax", ITIS_TSN_SARDINOPS_SAGAX, 10, 2.5)
        )
        assert parsed is not None
        self.assertEqual(parsed.total_number, 10)
        self.assertAlmostEqual(parsed.total_weight_kg or 0.0, 2.5)

    def test_catch_row_without_measurement_is_invalid(self) -> None:
        self.assertTrue(
            catch_row_invalid(_catch_row(1, "Sardinops sagax", ITIS_TSN_SARDINOPS_SAGAX, None, None))
        )

    def test_fixture_transform_sets_and_catch(self) -> None:
        rows = [
            _catch_row(1, "Sardinops sagax", ITIS_TSN_SARDINOPS_SAGAX, 10, 2.5),
            _catch_row(1, "Engraulis mordax", ITIS_TSN_ENGRAULIS_MORDAX, 0, 0.0),
            _catch_row(2, "Sardinops sagax", ITIS_TSN_SARDINOPS_SAGAX, 5, 1.0),
        ]
        result = transform_rows(rows)
        self.assertEqual(len(result.sets), 2)
        self.assertEqual(len(result.catch), 3)
        self.assertEqual(result.sets[0]["set_id"], "CPSNearshore:209901:SY:1")
        # Purse-seine sets: effort duration is an explicit null with reason.
        self.assertIsNone(result.sets[0]["effort_duration_min"])
        self.assertEqual(
            result.sets[0]["effort_duration_null_reason"], "not_applicable_purse_seine_set"
        )

    def test_bad_coord_drops_set_once(self) -> None:
        rows = [
            _catch_row(1, "Sardinops sagax", ITIS_TSN_SARDINOPS_SAGAX, 10, 2.5),
            _catch_row(1, "Engraulis mordax", ITIS_TSN_ENGRAULIS_MORDAX, 4, 1.0),
        ]
        rows[0]["latitude"] = "999"
        rows[1]["latitude"] = "999"
        result = transform_rows(rows)
        self.assertEqual(len(result.sets), 0)
        self.assertEqual(result.dropped_sets, 1)

    def test_gate_blocks_without_evidence_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence_path = _evidence_yaml_tmp(Path(tmp), sets=[1])
            evidence = load_zero_frame_evidence(evidence_path)
            # Set 2 is not in the verified frame.
            may_zero, reason = set_zero_frame_status("CPSNearshore:209901:SY:2", evidence)
            self.assertFalse(may_zero)
            self.assertEqual(reason, SET_NOT_IN_VERIFIED_FRAME_REASON)

    def test_verified_set_emits_implied_zero(self) -> None:
        evidence = load_zero_frame_evidence(EVIDENCE_FIXTURE)
        catch = [
            {
                "set_id": "CPSNearshore:209901:SY:1",
                "scientific_name": "Sardinops sagax",
                "itis_tsn": ITIS_TSN_SARDINOPS_SAGAX,
            }
        ]
        matrix = expand_set_species_matrix(
            catch,
            ["CPSNearshore:209901:SY:1"],
            list(PILOT_SPECIES_ITIS_TSN),
            species_itis_tsn=dict(PILOT_SPECIES_ITIS_TSN),
            set_meta=[{"set_id": "CPSNearshore:209901:SY:1"}],
            evidence_path=EVIDENCE_FIXTURE,
            on_unverified="na",
        )
        by_species = {r["scientific_name"]: r for r in matrix}
        self.assertEqual(by_species["Sardinops sagax"]["encounter"], 1)
        self.assertEqual(by_species["Engraulis mordax"]["encounter"], 0)
        self.assertEqual(
            by_species["Engraulis mordax"]["evidence"], "implied_zero_verified_frame"
        )

    def test_unverified_set_emits_not_available_not_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence_path = _evidence_yaml_tmp(Path(tmp), sets=[1])
            matrix = expand_set_species_matrix(
                [],
                ["CPSNearshore:209901:SY:9"],
                list(PILOT_SPECIES_ITIS_TSN),
                species_itis_tsn=dict(PILOT_SPECIES_ITIS_TSN),
                set_meta=[{"set_id": "CPSNearshore:209901:SY:9"}],
                evidence_path=evidence_path,
                on_unverified="na",
            )
            for row in matrix:
                self.assertIsNone(row["encounter"])
                self.assertEqual(row["evidence"], "not_available")

    def test_unverified_set_with_error_mode_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence_path = _evidence_yaml_tmp(Path(tmp), sets=[1])
            with self.assertRaises(ZeroFrameUnverifiedError):
                expand_set_species_matrix(
                    [],
                    ["CPSNearshore:209901:SY:9"],
                    list(PILOT_SPECIES_ITIS_TSN),
                    species_itis_tsn=dict(PILOT_SPECIES_ITIS_TSN),
                    set_meta=[{"set_id": "CPSNearshore:209901:SY:9"}],
                    evidence_path=evidence_path,
                    on_unverified="error",
                )

    def test_pilot_species_itis_tsn_exact_values(self) -> None:
        self.assertEqual(PILOT_SPECIES_ITIS_TSN["Sardinops sagax"], 161729)
        self.assertEqual(PILOT_SPECIES_ITIS_TSN["Engraulis mordax"], 161828)

    def test_read_csv_skips_units_row(self) -> None:
        text = (
            "cruise,time,latitude,longitude,scientific_name,totalNumber,totalWeightkg\n"
            ",UTC,degrees_north,degrees_east,,,\n"
            "209901,2099-07-01T19:00:00Z,34.0,-120.0,Sardinops sagax,10,2.5\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "units.csv"
            path.write_text(text, encoding="utf-8")
            rows, skipped = read_cps_nearshore_csv(path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(skipped, 1)
        self.assertEqual(rows[0]["scientific_name"], "Sardinops sagax")

    def test_pipeline_writes_parquet_contracts(self) -> None:
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            self.skipTest("pyarrow not available")
        sets = [{"set_id": "CPSNearshore:209901:SY:1"}]
        catch: list[dict] = []
        matrix = nearshore_pipeline.build_set_species_matrix(
            sets, catch, evidence_path=EVIDENCE_FIXTURE
        )
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            sp, cp, mp = nearshore_pipeline.write_parquet_contracts(sets, catch, matrix, dest)
            self.assertTrue(sp.exists())
            self.assertTrue(cp.exists())
            self.assertTrue(mp.exists())


if __name__ == "__main__":
    unittest.main()
