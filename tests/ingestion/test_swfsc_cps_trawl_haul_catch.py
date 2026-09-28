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
    ITIS_TSN_SARDINOPS_SAGAX,
    PILOT_SPECIES_ITIS_TSN,
    UNPARSEABLE_CATCH_ROW_REASON,
    UNRESOLVED_HIGHER_TAXON_REASON,
    WEIGHT_FLAG_PARTIAL,
)
from fishai.ingestion.biology.cps_trawl import pipeline as cps_pipeline
from fishai.ingestion.biology.cps_trawl.taxonomy import SUBSPECIES_TSN_TO_SPECIES_TSN
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

TSN_SARDINOPS_SAGAX = ITIS_TSN_SARDINOPS_SAGAX
TSN_ENGRAULIS_MORDAX = ITIS_TSN_ENGRAULIS_MORDAX
TSN_SARDINOPS_CAERULEA = next(
    k for k, v in SUBSPECIES_TSN_TO_SPECIES_TSN.items() if v == ITIS_TSN_SARDINOPS_SAGAX
)

SPECIES_TSN = dict(PILOT_SPECIES_ITIS_TSN)


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
            "itis_tsn": TSN_SARDINOPS_SAGAX,
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
                haul_meta=[{"haul_id": "CPSTrawl:209901:SY:1", "animalia_only_haul": False}],
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
        self.assertNotEqual(merged.weight_kg, 0.0)
        self.assertEqual(merged.weight_null_reason, "weights_missing")


def _collection_split_missing_weight_rows() -> list[dict[str, str]]:
    base = {
        "cruise": "209901",
        "ship": "SY",
        "haul": "1",
        "latitude": "33.0",
        "longitude": "-120.0",
        "stop_latitude": "33.02",
        "stop_longitude": "-119.98",
        "time": "2099-06-01T12:00:00Z",
        "haulback_time": "2099-06-01T12:30:00Z",
        "scientific_name": "Sardinops sagax",
        "itis_tsn": str(ITIS_TSN_SARDINOPS_SAGAX),
        "subsample_weight": "NaN",
        "remaining_weight": "NaN",
        "presence_only": "N",
    }
    return [
        {**base, "collection": "1", "subsample_count": "5"},
        {**base, "collection": "2", "subsample_count": "3"},
    ]


class CpsTrawlSyncMissingWeightTests(unittest.TestCase):
    def test_sync_collection_merge_missing_weight_stays_null(self) -> None:
        rows = _collection_split_missing_weight_rows()
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
            catch_path = Path(result["catch_path"])
            self.assertTrue(catch_path.is_file())
            table = pq.read_table(catch_path)
            records = table.to_pylist()
            sard = next(r for r in records if r["species"] == "Sardinops sagax")
            self.assertIsNone(sard["weight_kg"])
            self.assertNotEqual(sard["weight_kg"], 0.0)
            self.assertEqual(sard["subsample_count"], 8)
            qc = json.loads(Path(result["qc_report_path"]).read_text(encoding="utf-8"))
            self.assertEqual(qc["catch_rows_kept"], 1)


class CpsTrawlPilotItisTsnTests(unittest.TestCase):
    def test_pilot_species_itis_tsn_exact_values(self) -> None:
        self.assertEqual(PILOT_SPECIES_ITIS_TSN["Sardinops sagax"], 161729)
        self.assertEqual(PILOT_SPECIES_ITIS_TSN["Engraulis mordax"], 161828)
        self.assertEqual(ITIS_TSN_SARDINOPS_SAGAX, 161729)
        self.assertEqual(ITIS_TSN_ENGRAULIS_MORDAX, 161828)


class CpsTrawlHigherTaxonGapTests(unittest.TestCase):
    """auditbot1: order/family/unid/larvae patterns must block implied zeros."""

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

    def test_subspecies_tsn_suppresses_implied_zero_for_species(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            matrix = expand_haul_species_matrix(
                [
                    {
                        "haul_id": "CPSTrawl:209901:SY:1",
                        "species": "Sardinops sagax caerulea",
                        "itis_tsn": TSN_SARDINOPS_CAERULEA,
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
                "itis_tsn": str(TSN_ENGRAULIS_MORDAX),
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
                        "itis_tsn": TSN_ENGRAULIS_MORDAX,
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
    table = pq.read_table(result["matrix_path"])
    return table.to_pylist()


class CpsTrawlSyncZeroFrameGateTests(unittest.TestCase):
    """False-zero gates must run inside ``sync_cps_trawl_haul_catch`` (production path)."""

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
                "itis_tsn": str(TSN_ENGRAULIS_MORDAX),
                "subsample_count": "2",
                "subsample_weight": "1.0",
                "remaining_weight": "1.0",
                "presence_only": "N",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp), hauls=[3])
            proc = Path(tmp) / "processed"
            result = _run_sync_cps_trawl(rows, evidence, proc)
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
            proc = Path(tmp) / "processed"
            result = _run_sync_cps_trawl(rows, evidence, proc)
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
                "itis_tsn": str(TSN_ENGRAULIS_MORDAX),
                "subsample_count": "2",
                "subsample_weight": "1.0",
                "remaining_weight": "1.0",
                "presence_only": "N",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            evidence = _evidence_yaml_tmp(Path(tmp))
            proc = Path(tmp) / "processed"
            with mock.patch.object(cps_pipeline, "haul_meta_for_matrix", return_value=[]):
                result = _run_sync_cps_trawl(rows, evidence, proc)
            matrix = _matrix_rows(result)
        sard = next(m for m in matrix if m["species"] == "Sardinops sagax")
        self.assertEqual(sard["fill_reason"], HAUL_META_MISSING_REASON)
        self.assertFalse(sard["is_implied_zero"])


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
