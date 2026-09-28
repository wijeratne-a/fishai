"""Schema sample conformance tests — tiny synthetic JSON only; no coordinates printed."""

from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = REPO_ROOT / "src" / "fishai" / "schemas"
AUDIT = REPO_ROOT / "docs" / "archive" / "audit" / "contracts"


def load_schema(name: str) -> dict:
    with (SCHEMAS / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def validate(schema_name: str, instance: dict) -> list[str]:
    schema = load_schema(schema_name)
    validator = jsonschema.Draft7Validator(schema)
    return sorted(e.message for e in validator.iter_errors(instance))


# --- synthetic samples (no native coordinates) ---

SYN_SOURCE_RVC = {
    "source_id": "syn_rvc_atlantic",
    "source_name": "Synthetic Atlantic RVC",
    "source_family": "STRUCTURED_SURVEY",
    "record_kind": "BIOLOGICAL_OBSERVATION",
    "protocol_id": "RVC_STATIONARY_PLOT",
    "rights_status": "APPROVED_WITH_ATTRIBUTION",
    "license": "CC-BY-4.0",
    "presence_only": False,
    "supports_survey_nondetection": True,
    "coordinate_policy": "NATIVE_PRIVATE_ONLY",
}

SYN_SOURCE_OBIS = {
    "source_id": "syn_obis_presence",
    "source_name": "Synthetic OBIS presence",
    "source_family": "COMPILED_OCCURRENCE",
    "record_kind": "BIOLOGICAL_OBSERVATION",
    "protocol_id": "OBIS_OCCURRENCE",
    "rights_status": "APPROVED_WITH_ATTRIBUTION",
    "license": "CC-BY-4.0",
    "presence_only": True,
    "supports_survey_nondetection": False,
    "coordinate_policy": "COARSEN_BEFORE_PUBLIC",
}

SYN_SOURCE_SST = {
    "source_id": "syn_mur_sst",
    "source_name": "Synthetic MUR SST",
    "source_family": "REMOTE_ENVIRONMENTAL",
    "record_kind": "ENVIRONMENTAL_CONDITION",
    "protocol_id": "MUR_ANALYSED_SST",
    "rights_status": "APPROVED_OPEN_COMMERCIAL",
    "license": "OPEN",
    "presence_only": False,
    "supports_survey_nondetection": False,
    "coordinate_policy": "PUBLIC_CELL_ONLY",
}

SYN_EVENT = {
    "event_id": "syn-event-1",
    "source_id": "syn_rvc_atlantic",
    "protocol_id": "RVC_STATIONARY_PLOT",
    "observed_at_utc": "2023-06-15T12:00:00Z",
    "time_precision": "DAY",
    "spatial_support": "SAMPLE_UNIT",
    "latitude": None,
    "longitude": None,
    "spatial_cell_id": "cell-syn-001",
    "privacy_tier": "PUBLIC",
}

SYN_EFFORT = {
    "effort_id": "syn-effort-1",
    "event_id": "syn-event-1",
    "source_id": "syn_rvc_atlantic",
    "protocol_id": "RVC_STATIONARY_PLOT",
    "effort_type": "VISUAL_PLOT",
    "effort_completed": True,
}

SYN_OBS_DETECTION = {
    "observation_id": "syn-obs-det-1",
    "event_id": "syn-event-1",
    "source_id": "syn_rvc_atlantic",
    "taxon_id": "urn:lsid:marinespecies.org:taxname:1",
    "observation_state": "CONFIRMED_PRESENCE",
    "evidence_class": "STRUCTURED_SURVEY_DETECTION",
    "time_precision": "DAY",
    "is_absence_claim": False,
    "privacy_tier": "PUBLIC",
    "count_or_index_value": 0.75,
    "count_or_index_unit": "REAL_VALUED_AVERAGE",
}

SYN_OBS_NONDETECTION = {
    "observation_id": "syn-obs-nd-1",
    "event_id": "syn-event-1",
    "source_id": "syn_rvc_atlantic",
    "taxon_id": "urn:lsid:marinespecies.org:taxname:1",
    "observation_state": "SURVEY_NONDETECTION",
    "evidence_class": "SURVEY_NONDETECTION",
    "time_precision": "DAY",
    "effort_id": "syn-effort-1",
    "is_absence_claim": False,
    "privacy_tier": "PUBLIC",
    "count_or_index_value": 0.0,
    "count_or_index_unit": "REAL_VALUED_AVERAGE",
}

SYN_OBS_PRESENCE_ONLY = {
    "observation_id": "syn-obs-po-1",
    "event_id": "syn-event-obis-1",
    "source_id": "syn_obis_presence",
    "taxon_id": "urn:lsid:marinespecies.org:taxname:1",
    "observation_state": "PRESENCE_ONLY_NO_ABSENCE",
    "evidence_class": "HISTORICAL_OCCURRENCE",
    "time_precision": "DAY",
    "is_absence_claim": False,
    "privacy_tier": "COARSENED",
}

SYN_MEAS_NUM = {
    "measurement_id": "syn-meas-num-1",
    "subject_kind": "BIOLOGICAL",
    "measurement_type": "num_index",
    "measurement_value": 0.75,
    "measurement_unit": "REAL_VALUED_AVERAGE",
    "time_precision": "DAY",
}

SYN_MEAS_SST = {
    "measurement_id": "syn-meas-sst-1",
    "subject_kind": "ENVIRONMENTAL",
    "measurement_type": "sea_surface_temperature",
    "measurement_value": 28.1,
    "measurement_unit": "deg_C",
    "time_precision": "DAY",
}

SYN_TAXON = {
    "taxon_id": "urn:lsid:marinespecies.org:taxname:1",
    "aphia_id": 1,
    "scientific_name": "Syntheticus fishus",
    "taxonomic_authority": "WoRMS",
}

SYN_PROV = {
    "provenance_id": "syn-prov-1",
    "source_id": "syn_rvc_atlantic",
    "ingestion_run_id": "run-syn-1",
    "raw_payload_reference": "s3://synthetic/raw/payload.bin",
    "transformation_version": "v0",
    "transform_hash": "abc123",
    "source_checksum": "def456",
    "ingested_at_utc": "2026-09-24T00:00:00Z",
    "rights_status": "APPROVED_WITH_ATTRIBUTION",
}

SYN_GLOBE_EVIDENCE = {
    "evidence_id": "syn-ge-1",
    "evidence_label": "HISTORICAL_OCCURRENCE",
    "spatial_cell_id": "cell-syn-001",
    "time_precision": "DAY",
    "privacy_tier": "PUBLIC",
    "taxon_id": "urn:lsid:marinespecies.org:taxname:1",
    "user_visible_limitations": "Historical report only; not a current location.",
    "fishing_guidance": False,
}

SYN_MODEL_INTERNAL = {
    "output_id": "syn-mo-1",
    "taxon_id": "urn:lsid:marinespecies.org:taxname:1",
    "prediction_target": "occurrence_probability",
    "scientific_status": "historical_pattern",
    "publish_status": "NOT_PUBLISHED",
    "output_class": "INTERNAL_MODEL_OUTPUT",
    "spatial_cell_id": "cell-syn-001",
    "time_precision": "YEAR",
    "model_version": "syn-v0",
    "privacy_tier": "RESTRICTED",
    "confidence_category": "none",
    "user_visible_limitations": "Internal baseline only; not a published nowcast.",
    "fishing_guidance": False,
    "minimum_sample_size": "THRESHOLD_REQUIRES_POWER_ANALYSIS",
}


class SchemaSampleConformanceTests(unittest.TestCase):
    def test_valid_core_samples_pass(self):
        cases = [
            ("source.schema.json", SYN_SOURCE_RVC),
            ("source.schema.json", SYN_SOURCE_OBIS),
            ("source.schema.json", SYN_SOURCE_SST),
            ("event.schema.json", SYN_EVENT),
            ("effort.schema.json", SYN_EFFORT),
            ("observation.schema.json", SYN_OBS_DETECTION),
            ("observation.schema.json", SYN_OBS_NONDETECTION),
            ("observation.schema.json", SYN_OBS_PRESENCE_ONLY),
            ("measurement.schema.json", SYN_MEAS_NUM),
            ("measurement.schema.json", SYN_MEAS_SST),
            ("taxon.schema.json", SYN_TAXON),
            ("provenance.schema.json", SYN_PROV),
            ("globe-evidence.schema.json", SYN_GLOBE_EVIDENCE),
            ("globe-model-output.schema.json", SYN_MODEL_INTERNAL),
        ]
        for schema_name, sample in cases:
            with self.subTest(schema=schema_name, sample=sample.get("source_id") or sample.get("observation_id") or sample.get("output_id") or sample.get("evidence_id") or sample.get("measurement_id") or sample.get("taxon_id") or sample.get("event_id") or sample.get("effort_id") or sample.get("provenance_id")):
                errors = validate(schema_name, sample)
                self.assertEqual(errors, [], errors)

    def test_absence_claim_rejected(self):
        bad = dict(SYN_OBS_NONDETECTION)
        bad["is_absence_claim"] = True
        errors = validate("observation.schema.json", bad)
        self.assertTrue(errors)

    def test_globe_latitude_forbidden(self):
        bad = dict(SYN_GLOBE_EVIDENCE)
        bad["latitude"] = 18.0  # synthetic; never printed in assertions beyond failure
        errors = validate("globe-evidence.schema.json", bad)
        self.assertTrue(errors)

    def test_not_published_cannot_be_published_nowcast(self):
        bad = dict(SYN_MODEL_INTERNAL)
        bad["output_class"] = "PUBLISHED_NOWCAST"
        errors = validate("globe-model-output.schema.json", bad)
        self.assertTrue(errors)

    def test_num_average_not_integer_unit_in_sample(self):
        """NUM conflict: synthetic average must not pretend to be an integer count."""
        self.assertEqual(SYN_MEAS_NUM["measurement_unit"], "REAL_VALUED_AVERAGE")
        self.assertIsInstance(SYN_OBS_DETECTION["count_or_index_value"], float)
        self.assertNotEqual(SYN_OBS_DETECTION["count_or_index_unit"], "INTEGER_FISH_COUNT")

    def test_obis_presence_not_rvc_nondetection(self):
        self.assertTrue(SYN_SOURCE_OBIS["presence_only"])
        self.assertFalse(SYN_SOURCE_OBIS["supports_survey_nondetection"])
        self.assertEqual(SYN_OBS_PRESENCE_ONLY["observation_state"], "PRESENCE_ONLY_NO_ABSENCE")
        self.assertNotEqual(SYN_OBS_PRESENCE_ONLY["evidence_class"], "SURVEY_NONDETECTION")

    def test_sst_measurement_not_biological_observation(self):
        self.assertEqual(SYN_MEAS_SST["subject_kind"], "ENVIRONMENTAL")
        self.assertEqual(SYN_SOURCE_SST["record_kind"], "ENVIRONMENTAL_CONDITION")

    def test_conflict_catalog_lists_num_and_obis_rvc(self):
        path = AUDIT / "FIELD_SEMANTIC_CONFLICTS.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        ids = {row["conflict_id"] for row in rows}
        self.assertIn("C-NUM-01", ids)
        self.assertIn("C-OBIS-RVC-01", ids)
        self.assertIn("C-ZERO-ABSENCE-01", ids)

    def test_conformance_results_csv_exists(self):
        path = AUDIT / "CONFORMANCE_RESULTS.csv"
        with path.open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreaterEqual(len(rows), 10)
        results = {row["result"] for row in rows}
        self.assertIn("PASS", results)
        self.assertIn("FAIL", results)


if __name__ == "__main__":
    unittest.main()
