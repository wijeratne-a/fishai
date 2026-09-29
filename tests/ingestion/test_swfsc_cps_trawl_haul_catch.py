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
    HAUL_META_MISSING_REASON,
    ITIS_TSN_ENGRAULIS_MORDAX,
    ITIS_TSN_ENGRAULIS_NANUS,
    ITIS_TSN_OSTEICHTHYES,
    ITIS_TSN_SARDINOPS_CAERULEUS,
    ITIS_TSN_SARDINOPS_SAGAX,
    PILOT_SPECIES_ITIS_TSN,
    UNPARSEABLE_CATCH_ROW_REASON,
    UNRESOLVED_HIGHER_TAXON_REASON,
    WEIGHT_FLAG_PARTIAL,
)
from fishai.ingestion.biology.cps_trawl import pipeline as cps_pipeline
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

SPECIES_TSN = dict(PILOT_SPECIES_ITIS_TSN)
# ITIS TSN 623656 is Mentodus longirostris (not Sardinops); used for non-blocking regression tests.
ITIS_TSN_MENTODUS_LONGIROSTRIS = 623656
# Corrupt anchovy TSN seen in source data (typo padding); must fail closed on implied zeros.
ITIS_TSN_CORRUPT_ENGRAULIS_MORDAX = 16182800


def _evidence_yaml_tmp(tmpdir: Path, *, hauls: list[int] = [1]) -> Path:
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
                        "report_haul_log": hauls,
                        "aborted_tows": [],
                        "expected_hauls": hauls,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


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
            "itis_tsn": ITIS_TSN_SARDINOPS_SAGAX,
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
                species_itis_tsn=SPECIES_TSN,
                evidence_path=self.empty_evidence,
                on_unverified="raise",
            )

    def test_unexplained_haul_number_blocked(self) -> None:
        with self.assertRaises(ZeroFrameUnverifiedError) as ctx:
            expand_haul_species_matrix(
                [],
                ["CPSTrawl:209901:SY:99"],
                ["Sardinops sagax"],
                species_itis_tsn=SPECIES_TSN,
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
            species_itis_tsn=SPECIES_TSN,
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
            species_itis_tsn=SPECIES_TSN,
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


class CpsTrawlPilotItisTsnTests(unittest.TestCase):
    def test_pilot_species_itis_tsn_exact_values(self) -> None:
        self.assertEqual(PILOT_SPECIES_ITIS_TSN["Sardinops sagax"], 161729)
        self.assertEqual(PILOT_SPECIES_ITIS_TSN["Engraulis mordax"], 161828)
        self.assertEqual(ITIS_TSN_SARDINOPS_SAGAX, 161729)
        self.assertEqual(ITIS_TSN_ENGRAULIS_MORDAX, 161828)


class CpsTrawlHigherTaxonGapTests(unittest.TestCase):
    def _assert_blocks_sardine_zero(self, scientific_name: str, itis_tsn: int = 999001) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = expand_haul_species_matrix(
                [
                    {
                        "haul_id": "CPSTrawl:209901:SY:1",
                        "species": scientific_name,
                        "itis_tsn": itis_tsn,
                        "subsample_count": 1,
                        "weight_kg": None,
                        "presence_only": False,
                    }
                ],
                ["CPSTrawl:209901:SY:1"],
                ["Sardinops sagax", "Engraulis mordax"],
                species_itis_tsn=SPECIES_TSN,
                evidence_path=evidence,
                haul_meta=[{"haul_id": "CPSTrawl:209901:SY:1", "animalia_only_haul": False}],
                on_unverified="na",
            )
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertEqual(sard["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
        self.assertFalse(sard["is_implied_zero"])

    def test_order_clupeiformes_blocks_zero(self) -> None:
        self._assert_blocks_sardine_zero("Clupeiformes")

    def test_family_idae_suffix_case_insensitive_blocks_zero(self) -> None:
        self._assert_blocks_sardine_zero("clupeidae")

    def test_unid_token_blocks_zero(self) -> None:
        self._assert_blocks_sardine_zero("Clupeid unid.")

    def test_unidentified_in_name_blocks_zero(self) -> None:
        self._assert_blocks_sardine_zero("unidentified clupeid")

    def test_larvae_in_name_blocks_zero(self) -> None:
        self._assert_blocks_sardine_zero("Sardinops sagax larvae")

    def test_genus_only_name_blocks_zero(self) -> None:
        self._assert_blocks_sardine_zero("Sardinops", itis_tsn=999010)


class CpsTrawlFalseZeroGapTests(unittest.TestCase):
    """Dedicated tests for haul_meta, TSN matching, and unparseable catch rows."""

    def test_haul_meta_missing_blocks_zero_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = expand_haul_species_matrix(
                [],
                ["CPSTrawl:209901:SY:1"],
                ["Sardinops sagax"],
                species_itis_tsn=SPECIES_TSN,
                evidence_path=evidence,
                haul_meta=None,
                on_unverified="na",
            )
        self.assertEqual(matrix[0]["fill_reason"], HAUL_META_MISSING_REASON)

    def test_haul_meta_missing_entry_blocks_animalia_only_haul(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = expand_haul_species_matrix(
                [
                    {
                        "haul_id": "CPSTrawl:209901:SY:1",
                        "species": "Animalia",
                        "itis_tsn": None,
                        "subsample_count": None,
                        "presence_only": False,
                    }
                ],
                ["CPSTrawl:209901:SY:1"],
                ["Sardinops sagax"],
                species_itis_tsn=SPECIES_TSN,
                evidence_path=evidence,
                haul_meta=[],
                on_unverified="na",
            )
        self.assertEqual(matrix[0]["fill_reason"], HAUL_META_MISSING_REASON)

    def test_itis_junior_synonym_tsn_suppresses_implied_zero_for_sardine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = expand_haul_species_matrix(
                [
                    {
                        "haul_id": "CPSTrawl:209901:SY:1",
                        "species": "Sardinops caeruleus",
                        "itis_tsn": ITIS_TSN_SARDINOPS_CAERULEUS,
                        "subsample_count": 3,
                        "count_raised_est": 3,
                        "weight_kg": 1.0,
                        "presence_only": False,
                    }
                ],
                ["CPSTrawl:209901:SY:1"],
                ["Sardinops sagax", "Engraulis mordax"],
                species_itis_tsn=SPECIES_TSN,
                evidence_path=evidence,
                haul_meta=[{"haul_id": "CPSTrawl:209901:SY:1", "animalia_only_haul": False}],
            )
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertFalse(sard["is_implied_zero"])
        self.assertEqual(sard["subsample_count"], 3)
        anch = next(m for m in matrix if m["species"] == "Engraulis mordax")
        self.assertTrue(anch["is_implied_zero"])

    def test_mentodus_longirostris_tsn_does_not_block_sardine_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = expand_haul_species_matrix(
                [
                    {
                        "haul_id": "CPSTrawl:209901:SY:1",
                        "species": "Mentodus longirostris",
                        "itis_tsn": ITIS_TSN_MENTODUS_LONGIROSTRIS,
                        "subsample_count": 1,
                        "weight_kg": 1.0,
                        "presence_only": False,
                    }
                ],
                ["CPSTrawl:209901:SY:1"],
                ["Sardinops sagax", "Engraulis mordax"],
                species_itis_tsn=SPECIES_TSN,
                evidence_path=evidence,
                haul_meta=[{"haul_id": "CPSTrawl:209901:SY:1", "animalia_only_haul": False}],
            )
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertTrue(sard["is_implied_zero"])
        self.assertEqual(sard["fill_reason"], "verified_zero_frame")

    def test_unresolved_higher_taxon_blocks_target_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = expand_haul_species_matrix(
                [
                    {
                        "haul_id": "CPSTrawl:209901:SY:1",
                        "species": "Sardinops sp.",
                        "itis_tsn": 999001,
                        "subsample_count": 1,
                        "weight_kg": None,
                        "presence_only": False,
                    }
                ],
                ["CPSTrawl:209901:SY:1"],
                ["Sardinops sagax", "Engraulis mordax"],
                species_itis_tsn=SPECIES_TSN,
                evidence_path=evidence,
                haul_meta=[{"haul_id": "CPSTrawl:209901:SY:1", "animalia_only_haul": False}],
                on_unverified="na",
            )
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertEqual(sard["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
        anch = next(m for m in matrix if m["species"] == "Engraulis mordax")
        self.assertTrue(anch["is_implied_zero"])

    def test_transform_counts_unparseable_rows(self) -> None:
        rows = [
            {
                "cruise": "209901",
                "ship": "SY",
                "haul": "3",
                "latitude": "33.0",
                "longitude": "-120.0",
                "stop_latitude": "33.02",
                "stop_longitude": "-119.98",
                "time": "2099-06-01T12:00:00Z",
                "haulback_time": "2099-06-01T12:30:00Z",
                "scientific_name": "",
                "subsample_count": "1",
                "subsample_weight": "1.0",
                "remaining_weight": "1.0",
                "presence_only": "N",
            },
            {
                "cruise": "209901",
                "ship": "SY",
                "haul": "3",
                "latitude": "33.0",
                "longitude": "-120.0",
                "stop_latitude": "33.02",
                "stop_longitude": "-119.98",
                "time": "2099-06-01T12:00:00Z",
                "haulback_time": "2099-06-01T12:30:00Z",
                "scientific_name": "Engraulis mordax",
                "itis_tsn": str(ITIS_TSN_ENGRAULIS_MORDAX),
                "subsample_count": "2",
                "subsample_weight": "1.0",
                "remaining_weight": "1.0",
                "presence_only": "N",
            },
        ]
        result = transform_rows(rows)
        haul = result.hauls[0]
        self.assertEqual(haul["unparseable_catch_rows"], 1)
        self.assertEqual(result.qc_report["unparseable_catch_rows_dropped"], 1)

    def test_unparseable_catch_row_blocks_haul_zeros_e2e(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp), hauls=[3])
            matrix = expand_haul_species_matrix(
                [
                    {
                        "haul_id": "CPSTrawl:209901:SY:3",
                        "species": "Engraulis mordax",
                        "itis_tsn": ITIS_TSN_ENGRAULIS_MORDAX,
                        "subsample_count": 2,
                        "weight_kg": 2.0,
                        "presence_only": False,
                    }
                ],
                ["CPSTrawl:209901:SY:3"],
                ["Sardinops sagax", "Engraulis mordax"],
                species_itis_tsn=SPECIES_TSN,
                evidence_path=evidence,
                haul_meta=[
                    {
                        "haul_id": "CPSTrawl:209901:SY:3",
                        "animalia_only_haul": False,
                        "unparseable_catch_rows": 1,
                    }
                ],
                on_unverified="na",
            )
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertEqual(sard["fill_reason"], UNPARSEABLE_CATCH_ROW_REASON)


def _run_sync_cps_trawl(
    rows: list[dict[str, str]],
    evidence: Path,
    proc: Path,
) -> dict:
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
        return sync_cps_trawl_haul_catch(
            date(2099, 1, 1),
            date(2099, 12, 31),
            fetch=False,
            evidence_path=evidence,
        )


def _matrix_rows(result: dict) -> list[dict]:
    return pq.read_table(result["matrix_path"]).to_pylist()


class CpsTrawlSyncZeroFrameGateTests(unittest.TestCase):
    def test_sync_blocks_unparseable_catch_row_zero(self) -> None:
        rows = [
            {
                "cruise": "209901",
                "ship": "SY",
                "haul": "3",
                "latitude": "33.0",
                "longitude": "-120.0",
                "stop_latitude": "33.02",
                "stop_longitude": "-119.98",
                "time": "2099-06-01T12:00:00Z",
                "haulback_time": "2099-06-01T12:30:00Z",
                "scientific_name": "",
                "subsample_count": "1",
                "subsample_weight": "1.0",
                "remaining_weight": "1.0",
                "presence_only": "N",
            },
            {
                "cruise": "209901",
                "ship": "SY",
                "haul": "3",
                "latitude": "33.0",
                "longitude": "-120.0",
                "stop_latitude": "33.02",
                "stop_longitude": "-119.98",
                "time": "2099-06-01T12:00:00Z",
                "haulback_time": "2099-06-01T12:30:00Z",
                "scientific_name": "Engraulis mordax",
                "itis_tsn": str(ITIS_TSN_ENGRAULIS_MORDAX),
                "subsample_count": "2",
                "subsample_weight": "1.0",
                "remaining_weight": "1.0",
                "presence_only": "N",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp), hauls=[3])
            result = _run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed")
            matrix = _matrix_rows(result)
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertEqual(sard["fill_reason"], UNPARSEABLE_CATCH_ROW_REASON)
        self.assertFalse(sard["is_implied_zero"])

    def test_sync_blocks_unresolved_higher_taxon_zero(self) -> None:
        rows = [
            {
                "cruise": "209901",
                "ship": "SY",
                "haul": "1",
                "latitude": "33.0",
                "longitude": "-120.0",
                "stop_latitude": "33.02",
                "stop_longitude": "-119.98",
                "time": "2099-06-01T12:00:00Z",
                "haulback_time": "2099-06-01T12:30:00Z",
                "scientific_name": "Sardinops sp.",
                "itis_tsn": "999001",
                "subsample_count": "1",
                "subsample_weight": "1.0",
                "remaining_weight": "1.0",
                "presence_only": "N",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            result = _run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed")
            matrix = _matrix_rows(result)
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertEqual(sard["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
        anch = next(m for m in matrix if m["species"] == "Engraulis mordax")
        self.assertTrue(anch["is_implied_zero"])

    def test_sync_blocks_haul_meta_missing_zero(self) -> None:
        rows = [
            {
                "cruise": "209901",
                "ship": "SY",
                "haul": "1",
                "latitude": "33.0",
                "longitude": "-120.0",
                "stop_latitude": "33.02",
                "stop_longitude": "-119.98",
                "time": "2099-06-01T12:00:00Z",
                "haulback_time": "2099-06-01T12:30:00Z",
                "scientific_name": "Engraulis mordax",
                "itis_tsn": str(ITIS_TSN_ENGRAULIS_MORDAX),
                "subsample_count": "2",
                "subsample_weight": "1.0",
                "remaining_weight": "1.0",
                "presence_only": "N",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            with mock.patch.object(cps_pipeline, "haul_meta_for_matrix", return_value=[]):
                result = _run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed")
            matrix = _matrix_rows(result)
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertEqual(sard["fill_reason"], HAUL_META_MISSING_REASON)
        self.assertFalse(sard["is_implied_zero"])


class CpsTrawlSyncGenusAndNameTsnTests(unittest.TestCase):
    def _erddap_row(self, haul: str, scientific_name: str, itis_tsn: str) -> dict[str, str]:
        return {
            "cruise": "209901",
            "ship": "SY",
            "haul": haul,
            "latitude": "33.0",
            "longitude": "-120.0",
            "stop_latitude": "33.02",
            "stop_longitude": "-119.98",
            "time": "2099-06-01T12:00:00Z",
            "haulback_time": "2099-06-01T12:30:00Z",
            "scientific_name": scientific_name,
            "itis_tsn": itis_tsn,
            "subsample_count": "1",
            "subsample_weight": "1.0",
            "remaining_weight": "1.0",
            "presence_only": "N",
        }

    def test_sync_genus_only_sardinops_blocks_sardine_zero(self) -> None:
        rows = [self._erddap_row("1", "Sardinops", "999010")]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertEqual(sard["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
        self.assertFalse(sard["is_implied_zero"])
        anch = next(m for m in matrix if m["species"] == "Engraulis mordax")
        self.assertTrue(anch["is_implied_zero"])

    def test_sync_genus_only_engraulis_blocks_anchovy_zero(self) -> None:
        rows = [self._erddap_row("1", "Engraulis", "999011")]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        anch = next(m for m in matrix if m["species"] == "Engraulis mordax")
        self.assertEqual(anch["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
        self.assertFalse(anch["is_implied_zero"])
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertTrue(sard["is_implied_zero"])

    def test_sync_name_tsn_mismatch_blocks_target_zero(self) -> None:
        rows = [
            self._erddap_row("1", "Sardinops", str(ITIS_TSN_ENGRAULIS_MORDAX)),
            self._erddap_row("2", "Engraulis mordax", str(ITIS_TSN_SARDINOPS_SAGAX)),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp), hauls=[1, 2])
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        haul1 = [m for m in matrix if m["haul_id"].endswith(":1")]
        sard1 = next(m for m in haul1 if m["species"] == "Sardinops sagax")
        self.assertEqual(sard1["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
        self.assertFalse(sard1["is_implied_zero"])
        haul2 = [m for m in matrix if m["haul_id"].endswith(":2")]
        anch2 = next(m for m in haul2 if m["species"] == "Engraulis mordax")
        self.assertEqual(anch2["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
        self.assertFalse(anch2["is_implied_zero"])

    def test_sync_sardinops_caeruleus_synonym_counts_as_sardine_presence(self) -> None:
        rows = [
            self._erddap_row(
                "1",
                "Sardinops caeruleus",
                str(ITIS_TSN_SARDINOPS_CAERULEUS),
            )
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertFalse(sard["is_implied_zero"])
        self.assertEqual(sard["subsample_count"], 1)

    def test_sync_normalized_scientific_names_count_as_presence(self) -> None:
        rows = [
            self._erddap_row("1", "sardinops sagax", str(ITIS_TSN_SARDINOPS_SAGAX)),
            self._erddap_row(
                "2",
                "  Engraulis   mordax ",
                str(ITIS_TSN_ENGRAULIS_MORDAX),
            ),
            self._erddap_row(
                "3",
                "Sardinops sagax (Jenyns, 1842)",
                str(ITIS_TSN_SARDINOPS_SAGAX),
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp), hauls=[1, 2, 3])
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        haul1 = next(m for m in matrix if m["haul_id"].endswith(":1") and m["species"] == "Sardinops sagax")
        self.assertFalse(haul1["is_implied_zero"])
        haul2 = next(
            m for m in matrix if m["haul_id"].endswith(":2") and m["species"] == "Engraulis mordax"
        )
        self.assertFalse(haul2["is_implied_zero"])
        haul3 = next(m for m in matrix if m["haul_id"].endswith(":3") and m["species"] == "Sardinops sagax")
        self.assertFalse(haul3["is_implied_zero"])

    def test_sync_mentodus_longirostris_does_not_block_sardine_zero(self) -> None:
        rows = [
            self._erddap_row(
                "1",
                "Mentodus longirostris",
                str(ITIS_TSN_MENTODUS_LONGIROSTRIS),
            )
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertTrue(sard["is_implied_zero"])
        self.assertEqual(sard["fill_reason"], "verified_zero_frame")

    def test_sync_uncertain_id_qualifiers_block_pilot_species_zeros(self) -> None:
        # ITIS genus TSN 161728 = Sardinops; unrelated species TSNs exercise non-target IDs.
        sardinops_genus_tsn = "161728"
        engraulis_genus_tsn = "999011"
        sardine_cases = (
            ("Sardinops cf. sagax", sardinops_genus_tsn),
            ("Sardinops cf. sagax", str(ITIS_TSN_ENGRAULIS_MORDAX)),
            ("Sardinops aff. sagax", sardinops_genus_tsn),
            ("Sardinops aff. sagax", str(ITIS_TSN_ENGRAULIS_MORDAX)),
            ("Sardinops sagax?", sardinops_genus_tsn),
            ("Sardinops sagax?", str(ITIS_TSN_ENGRAULIS_MORDAX)),
            ("Sardinops ?sagax", sardinops_genus_tsn),
            ("Sardinops ?sagax", str(ITIS_TSN_ENGRAULIS_MORDAX)),
        )
        anchovy_cases = (
            ("Engraulis cf. mordax", engraulis_genus_tsn),
            ("Engraulis cf. mordax", str(ITIS_TSN_SARDINOPS_SAGAX)),
            ("Engraulis aff. mordax", engraulis_genus_tsn),
            ("Engraulis aff. mordax", str(ITIS_TSN_SARDINOPS_SAGAX)),
            ("Engraulis mordax?", engraulis_genus_tsn),
            ("Engraulis mordax?", str(ITIS_TSN_SARDINOPS_SAGAX)),
            ("Engraulis ?mordax", engraulis_genus_tsn),
            ("Engraulis ?mordax", str(ITIS_TSN_SARDINOPS_SAGAX)),
        )
        rows: list[dict[str, str]] = []
        haul_ids: list[int] = []
        haul = 1
        for scientific_name, itis_tsn in sardine_cases + anchovy_cases:
            rows.append(self._erddap_row(str(haul), scientific_name, itis_tsn))
            haul_ids.append(haul)
            haul += 1
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp), hauls=haul_ids)
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        for haul_num, (scientific_name, _) in enumerate(sardine_cases, start=1):
            haul_matrix = [m for m in matrix if m["haul_id"].endswith(f":{haul_num}")]
            sard = next(m for m in haul_matrix if m["species"] == "Sardinops sagax")
            with self.subTest(species="Sardinops sagax", name=scientific_name, haul=haul_num):
                self.assertEqual(sard["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
                self.assertFalse(sard["is_implied_zero"])
        offset = len(sardine_cases)
        for idx, (scientific_name, _) in enumerate(anchovy_cases, start=1):
            haul_num = offset + idx
            haul_matrix = [m for m in matrix if m["haul_id"].endswith(f":{haul_num}")]
            anch = next(m for m in haul_matrix if m["species"] == "Engraulis mordax")
            with self.subTest(species="Engraulis mordax", name=scientific_name, haul=haul_num):
                self.assertEqual(anch["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
                self.assertFalse(anch["is_implied_zero"])


class CpsTrawlSyncFalseZeroTaxonomyTests(unittest.TestCase):
    """Production sync path: parquet matrix fail-closed taxonomy gates."""

    def _erddap_row(self, haul: str, scientific_name: str, itis_tsn: str) -> dict[str, str]:
        return {
            "cruise": "209901",
            "ship": "SY",
            "haul": haul,
            "latitude": "33.0",
            "longitude": "-120.0",
            "stop_latitude": "33.02",
            "stop_longitude": "-119.98",
            "time": "2099-06-01T12:00:00Z",
            "haulback_time": "2099-06-01T12:30:00Z",
            "scientific_name": scientific_name,
            "itis_tsn": itis_tsn,
            "subsample_count": "1",
            "subsample_weight": "1.0",
            "remaining_weight": "1.0",
            "presence_only": "N",
        }

    def test_sync_osteichthyes_blocks_both_pilot_zeros(self) -> None:
        rows = [self._erddap_row("1", "Osteichthyes", str(ITIS_TSN_OSTEICHTHYES))]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        anch = next(m for m in matrix if m["species"] == "Engraulis mordax")
        self.assertEqual(sard["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
        self.assertEqual(anch["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
        self.assertFalse(sard["is_implied_zero"])
        self.assertFalse(anch["is_implied_zero"])

    def test_sync_engraulis_nanus_synonym_counts_as_anchovy_presence(self) -> None:
        rows = [
            self._erddap_row(
                "1",
                "Engraulis nanus",
                str(ITIS_TSN_ENGRAULIS_NANUS),
            )
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        anch = next(m for m in matrix if m["species"] == "Engraulis mordax")
        self.assertFalse(anch["is_implied_zero"])
        self.assertEqual(anch["subsample_count"], 1)
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertTrue(sard["is_implied_zero"])

    def test_sync_genus_sp_spp_variants_block_implied_zeros(self) -> None:
        cases = (
            ("1", "sardinops", "999010"),
            ("2", "Sardinops sp.", "999001"),
            ("3", "Sardinops SP.", "999002"),
            ("4", "Sardinops spp", "999003"),
            ("5", "Engraulis spp.", "999011"),
        )
        rows = [self._erddap_row(haul, name, tsn) for haul, name, tsn in cases]
        haul_ids = [int(haul) for haul, _, _ in cases]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp), hauls=haul_ids)
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        for haul, name, _ in cases:
            haul_matrix = [m for m in matrix if m["haul_id"].endswith(f":{haul}")]
            if name.casefold().startswith("sardinops") or name == "sardinops":
                sard = next(m for m in haul_matrix if m["species"] == "Sardinops sagax")
                with self.subTest(name=name):
                    self.assertEqual(sard["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
                    self.assertFalse(sard["is_implied_zero"])
            else:
                anch = next(m for m in haul_matrix if m["species"] == "Engraulis mordax")
                with self.subTest(name=name):
                    self.assertEqual(anch["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
                    self.assertFalse(anch["is_implied_zero"])

    def test_sync_corrupt_anchovy_tsn_blocks_implied_zero(self) -> None:
        rows = [
            self._erddap_row(
                "1",
                "Engraulis mordax",
                str(ITIS_TSN_CORRUPT_ENGRAULIS_MORDAX),
            )
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        anch = next(m for m in matrix if m["species"] == "Engraulis mordax")
        self.assertEqual(anch["fill_reason"], UNRESOLVED_HIGHER_TAXON_REASON)
        self.assertFalse(anch["is_implied_zero"])

    def test_sync_mentodus_longirostris_still_allows_sardine_zero(self) -> None:
        rows = [
            self._erddap_row(
                "1",
                "Mentodus longirostris",
                str(ITIS_TSN_MENTODUS_LONGIROSTRIS),
            )
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = _matrix_rows(_run_sync_cps_trawl(rows, evidence, Path(tmp) / "processed"))
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertTrue(sard["is_implied_zero"])
        self.assertEqual(sard["fill_reason"], "verified_zero_frame")


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
