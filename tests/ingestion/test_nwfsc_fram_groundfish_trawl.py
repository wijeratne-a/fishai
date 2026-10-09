"""Synthetic FRAM groundfish-trawl ingestion tests (no network)."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

import pyarrow.parquet as pq
import yaml

from fishai.ingestion.biology.fram_groundfish_trawl.constants import (
    API_BASE,
    CATCH_VARIABLES,
    SOURCE_ID,
)
from fishai.ingestion.biology.fram_groundfish_trawl.fetch import (
    FramVariableDropError,
    build_selection_url,
    load_raw_catch_for_window,
    load_raw_hauls_for_window,
    validate_response_variables,
)
from fishai.ingestion.biology.fram_groundfish_trawl import pipeline as fram_pipeline
from fishai.ingestion.biology.fram_groundfish_trawl.pipeline import sync_fram_groundfish_trawl
from fishai.ingestion.biology.fram_groundfish_trawl.trawl_id import survey_year_from_trawl_id
from fishai.ingestion.biology.fram_groundfish_trawl.transform import (
    make_tow_id,
    transform_rows,
)
from fishai.ingestion.sources import REPO_ROOT

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "fram_groundfish_trawl"


class FramTrawlIdTests(unittest.TestCase):
    def test_survey_year_from_trawl_id(self) -> None:
        self.assertEqual(survey_year_from_trawl_id(202503020168), 2025)
        self.assertIsNone(survey_year_from_trawl_id("abc"))

    def test_stable_tow_id(self) -> None:
        self.assertEqual(make_tow_id(209903008001), "FRAMGroundfishTrawl:209903008001")


class FramFetchUrlTests(unittest.TestCase):
    def test_build_selection_url_uses_trips_api_base(self) -> None:
        url = build_selection_url(
            "trawl.catch_fact",
            filters=["date_dim$year=2021"],
            variables=["trawl_id"],
        )
        self.assertTrue(url.startswith(API_BASE))
        self.assertIn("selection.json", url)
        self.assertIn("trawl_id", url)

    def test_validate_response_variables_detects_silent_drop(self) -> None:
        with self.assertRaises(FramVariableDropError):
            validate_response_variables(
                [{"trawl_id": 1}],
                CATCH_VARIABLES,
                layer="trawl.catch_fact",
            )


class FramTransformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catch = load_raw_catch_for_window(date(2099, 1, 1), date(2099, 12, 31), FIXTURES)
        cls.hauls = load_raw_hauls_for_window(date(2099, 1, 1), date(2099, 12, 31), FIXTURES)

    def test_transform_keeps_valid_bycatch_and_flags_missing_cpue(self) -> None:
        out = transform_rows(self.catch, self.hauls)
        self.assertEqual(out.qc_report["catch_rows_kept"], 2)
        self.assertEqual(len(out.hauls), 2)
        anchovy = next(r for r in out.catch if r["scientific_name"] == "Engraulis mordax")
        self.assertTrue(anchovy["presence_only"])
        self.assertEqual(anchovy["cpue_kg_per_ha_null_reason"], "missing_in_source_row")
        self.assertGreater(out.qc_report["dropped_by_rule"]["performance_excluded"], 0)

    def test_haul_join_includes_effort_metadata(self) -> None:
        out = transform_rows(self.catch, self.hauls)
        haul = next(h for h in out.hauls if h["trawl_id"] == 209903008001)
        self.assertAlmostEqual(haul["area_swept_ha"] or 0, 2.0)
        self.assertEqual(haul["survey_year"], 2099)


class FramSyncTests(unittest.TestCase):
    def test_sync_from_fixtures_writes_parquet(self) -> None:
        manifest = {
            "sources": {
                SOURCE_ID: {
                    "module": "fishai.ingestion.biology.nwfsc_fram_groundfish_trawl",
                    "license": "U.S. Government Work",
                    "license_url": "https://www.noaa.gov/information-technology/foia",
                    "attribution": "NOAA NWFSC FRAM",
                    "status": "approved",
                    "enabled": True,
                }
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw = tmp_path / "raw"
            shutil.copytree(FIXTURES, raw)
            processed = tmp_path / "processed"
            manifest_path = tmp_path / "SOURCES.yaml"
            manifest_path.write_text(yaml.dump(manifest), encoding="utf-8")

            with mock.patch.object(fram_pipeline, "raw_dir", return_value=raw), mock.patch.object(
                fram_pipeline, "processed_dir", return_value=processed
            ):
                result = sync_fram_groundfish_trawl(
                    date(2099, 1, 1),
                    date(2099, 12, 31),
                    fetch=False,
                    manifest_path=manifest_path,
                )

            self.assertEqual(result["n_catch_rows"], 2)
            catch_table = pq.read_table(result["catch_path"])
            self.assertIn("cpue_kg_per_ha", catch_table.column_names)
            meta = json.loads((processed / "fram_groundfish_trawl_metadata.json").read_text())
            self.assertIn("pelagic_bycatch_bias", meta)
            self.assertFalse(meta["implied_zeros"])


class FramManifestTests(unittest.TestCase):
    def test_sources_yaml_lists_fram_module(self) -> None:
        data = yaml.safe_load((REPO_ROOT / "data" / "SOURCES.yaml").read_text(encoding="utf-8"))
        entry = data["sources"][SOURCE_ID]
        self.assertEqual(entry["module"], "fishai.ingestion.biology.nwfsc_fram_groundfish_trawl")
        self.assertEqual(entry["status"], "approved")
