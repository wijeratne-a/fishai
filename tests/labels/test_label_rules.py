"""WS41/WS42 label validation tests — synthetic rows only; no real coordinates."""

from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
LABELS = REPO_ROOT / "labels"
SCIENCE = REPO_ROOT / "science"

NON_DETECTION_OUTCOMES = {
    "EXPLICIT_SURVEY_NONDETECTION",
    "CONSTRUCTED_SURVEY_NONDETECTION",
}


def load_rules() -> dict:
    with (LABELS / "LABEL_VALIDATION_RULES.yaml").open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def validate_label(row: dict, rules: dict | None = None) -> list[str]:
    """Return a list of validation error strings; empty means accept."""
    rules = rules or load_rules()
    errors: list[str] = []
    outcome = row.get("observation_outcome")
    req = rules["non_detection_requirements"]

    if row.get("is_ecological_absence_claim") is True:
        errors.append("ecological_absence_claim_forbidden")

    if outcome in NON_DETECTION_OUTCOMES:
        if row.get("event_completed") is not True:
            errors.append("non_detection_requires_completed_event")
        if row.get("event_frame_complete") is not True:
            errors.append("non_detection_requires_complete_event_frame")
        if row.get("zero_semantics_documented") is not True:
            errors.append("non_detection_requires_documented_zero_semantics")
        for field in req["required_non_empty_fields"]:
            value = row.get(field)
            if value is None or str(value).strip() == "":
                errors.append(f"non_detection_requires_{field}")
        zero_prov = row.get("zero_provenance")
        if zero_prov in req["forbidden_zero_provenance"]:
            errors.append(f"forbidden_zero_provenance:{zero_prov}")
        if zero_prov not in req["allowed_zero_provenance"]:
            errors.append(f"zero_provenance_not_allowed_for_nondetection:{zero_prov}")
        if row.get("evidence_tier") == "ENVIRONMENTAL_COVARIATE":
            errors.append("environmental_covariate_is_not_nondetection")
        if row.get("observation_method") == "HABITAT_OR_ENVIRONMENTAL_ONLY":
            errors.append("habitat_or_environment_is_not_nondetection")

    return errors


def atlantic_species_outcome(length_bin_nums: list[float], taxon_in_year_list: bool) -> str:
    """Collapse Atlantic RVC length bins to a species-level outcome (synthetic)."""
    if not taxon_in_year_list:
        return "NOT_EVALUATED"
    if any(n > 0 for n in length_bin_nums):
        return "DETECTED"
    if length_bin_nums and all(n == 0 for n in length_bin_nums):
        return "CONSTRUCTED_SURVEY_NONDETECTION"
    return "UNKNOWN"


def base_valid_nondetection(**overrides) -> dict:
    row = {
        "label_id": "syn-nd-1",
        "source_id": "CRCP_Reef_Fish_Surveys_Florida",
        "observation_outcome": "CONSTRUCTED_SURVEY_NONDETECTION",
        "observation_method": "REEF_VISUAL_CENSUS",
        "target_taxonomic_group": "SYNCODE1",
        "life_stage": "unknown",
        "count_type": "REAL_VALUED_AVERAGE",
        "effort_type": "VISUAL_PLOT",
        "taxonomic_confidence": "CONFIRMED",
        "identification_method": "VISUAL_FIELD",
        "observer_or_instrument_type": "TRAINED_DIVER",
        "spatial_precision": "SAMPLE_UNIT",
        "temporal_precision": "DAY",
        "protocol_version": "RVC_SYNTHETIC_v1",
        "quality_control_status": "PASSED",
        "zero_provenance": "CONSTRUCTED_FROM_COMPLETE_FRAME",
        "source_freshness": "HISTORICAL",
        "evidence_tier": "STRUCTURED_SURVEY",
        "event_completed": True,
        "event_frame_complete": True,
        "zero_semantics_documented": True,
        "is_ecological_absence_claim": False,
    }
    row.update(overrides)
    return row


class LabelArtifactPresence(unittest.TestCase):
    def test_required_files_exist(self):
        expected = [
            LABELS / "BIOLOGICAL_LABEL_SCHEMA.json",
            LABELS / "OBSERVATION_SEMANTICS.md",
            LABELS / "LABEL_VALIDATION_RULES.yaml",
            LABELS / "SOURCE_TO_LABEL_MAPPING.csv",
            LABELS / "LIFE_STAGE_ONTOLOGY.yaml",
            LABELS / "LIFE_STAGE_MAPPING.csv",
            SCIENCE / "life-stage" / "LIFE_STAGE_MODEL_RULES.md",
            SCIENCE / "MODEL_QUESTION_ROUTER.yaml",
        ]
        for path in expected:
            self.assertTrue(path.is_file(), msg=f"missing {path}")

    def test_schema_lists_required_outcomes(self):
        schema = json.loads((LABELS / "BIOLOGICAL_LABEL_SCHEMA.json").read_text(encoding="utf-8"))
        outcomes = set(schema["properties"]["observation_outcome"]["enum"])
        for name in NON_DETECTION_OUTCOMES | {
            "DETECTED",
            "REPORTED_ABSENT",
            "PRESENCE_ONLY",
            "NOT_EVALUATED",
            "UNKNOWN",
            "INVALID_EVENT",
        }:
            self.assertIn(name, outcomes)

    def test_source_mapping_covers_known_families(self):
        with (LABELS / "SOURCE_TO_LABEL_MAPPING.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        source_ids = {row["source_id"] for row in rows}
        for required in (
            "CRCP_Reef_Fish_Surveys_Florida",
            "CRCP_Reef_Fish_Surveys_Puerto_Rico",
            "CRCP_Reef_Fish_Surveys_USVI",
            "CRCP_Reef_Fish_Surveys_Flower_Gardens",
            "CRCP_Reef_Fish_Surveys_Hawaii",
            "OBIS_Keys_extract",
            "erdCalCOFIcufes",
        ):
            self.assertIn(required, source_ids)
        calcofi = next(r for r in rows if r["source_id"] == "erdCalCOFIcufes")
        self.assertEqual(calcofi["life_stage_default"], "egg")
        pacific = next(r for r in rows if r["source_id"] == "CRCP_Reef_Fish_Surveys_Hawaii")
        self.assertIn("PRESENCE_ONLY", pacific["observation_outcome_rule"])


class NonDetectionGate(unittest.TestCase):
    def setUp(self):
        self.rules = load_rules()

    def test_valid_constructed_nondetection_passes(self):
        self.assertEqual(validate_label(base_valid_nondetection(), self.rules), [])

    def test_fails_without_completed_event(self):
        errors = validate_label(base_valid_nondetection(event_completed=False), self.rules)
        self.assertIn("non_detection_requires_completed_event", errors)

    def test_fails_without_target_group(self):
        errors = validate_label(base_valid_nondetection(target_taxonomic_group=""), self.rules)
        self.assertIn("non_detection_requires_target_taxonomic_group", errors)

    def test_fails_without_protocol(self):
        errors = validate_label(base_valid_nondetection(protocol_version=""), self.rules)
        self.assertIn("non_detection_requires_protocol_version", errors)

    def test_fails_without_complete_frame(self):
        errors = validate_label(base_valid_nondetection(event_frame_complete=False), self.rules)
        self.assertIn("non_detection_requires_complete_event_frame", errors)

    def test_fails_without_documented_zero_semantics(self):
        errors = validate_label(
            base_valid_nondetection(zero_semantics_documented=False), self.rules
        )
        self.assertIn("non_detection_requires_documented_zero_semantics", errors)

    def test_single_length_bin_zero_not_species_result(self):
        # A lone NUM==0 bin is not itself CONSTRUCTED_SURVEY_NONDETECTION
        # until collapse rules and frame checks are applied via validate_label.
        row = base_valid_nondetection(
            zero_provenance="LENGTH_BIN_ROW_ONLY",
            observation_outcome="CONSTRUCTED_SURVEY_NONDETECTION",
        )
        errors = validate_label(row, self.rules)
        self.assertIn("forbidden_zero_provenance:LENGTH_BIN_ROW_ONLY", errors)

    def test_missing_row_not_nondetection(self):
        errors = validate_label(
            base_valid_nondetection(zero_provenance="MISSING_ROW"), self.rules
        )
        self.assertIn("forbidden_zero_provenance:MISSING_ROW", errors)

    def test_presence_only_gap_not_nondetection(self):
        errors = validate_label(
            base_valid_nondetection(zero_provenance="PRESENCE_ONLY_GAP"), self.rules
        )
        self.assertIn("forbidden_zero_provenance:PRESENCE_ONLY_GAP", errors)

    def test_sst_habitat_telemetry_citizen_acoustic_edna_not_absence(self):
        cases = [
            base_valid_nondetection(
                observation_method="HABITAT_OR_ENVIRONMENTAL_ONLY",
                evidence_tier="ENVIRONMENTAL_COVARIATE",
            ),
            base_valid_nondetection(
                observation_method="TELEMETRY",
                evidence_tier="TRACK_OR_TELEMETRY",
                zero_provenance="FORBIDDEN",
            ),
            base_valid_nondetection(
                observation_method="CITIZEN_SCIENCE",
                zero_provenance="UNDOCUMENTED",
            ),
            base_valid_nondetection(
                observation_method="ACOUSTIC_CLASSIFIER",
                zero_provenance="UNDOCUMENTED",
            ),
            base_valid_nondetection(
                observation_method="EDNA_ASSAY",
                zero_provenance="UNDOCUMENTED",
            ),
        ]
        for row in cases:
            errors = validate_label(row, self.rules)
            self.assertTrue(errors, msg=f"expected failure for {row['observation_method']}")

    def test_ecological_absence_flag_always_rejected(self):
        errors = validate_label(
            base_valid_nondetection(is_ecological_absence_claim=True), self.rules
        )
        self.assertIn("ecological_absence_claim_forbidden", errors)


class AtlanticLengthBinCollapse(unittest.TestCase):
    def test_any_positive_bin_is_detection(self):
        self.assertEqual(atlantic_species_outcome([0.0, 1.5, 0.0], True), "DETECTED")

    def test_all_zero_bins_on_list_is_constructed_nondetection(self):
        self.assertEqual(
            atlantic_species_outcome([0.0, 0.0], True),
            "CONSTRUCTED_SURVEY_NONDETECTION",
        )

    def test_taxon_not_on_year_list_is_not_evaluated(self):
        self.assertEqual(atlantic_species_outcome([0.0], False), "NOT_EVALUATED")

    def test_single_zero_row_needs_collapse_context(self):
        # One zero bin on-list collapses to constructed non-detection only after
        # treating the bin set as the full species result — still not ecological absence.
        outcome = atlantic_species_outcome([0.0], True)
        self.assertEqual(outcome, "CONSTRUCTED_SURVEY_NONDETECTION")
        errors = validate_label(
            base_valid_nondetection(
                observation_outcome=outcome,
                zero_provenance="LENGTH_BIN_ROW_ONLY",
            )
        )
        self.assertTrue(errors)


class LifeStageRules(unittest.TestCase):
    def test_ontology_forbids_definitive_length_alone(self):
        ontology = yaml.safe_load(
            (LABELS / "LIFE_STAGE_ONTOLOGY.yaml").read_text(encoding="utf-8")
        )
        self.assertFalse(ontology["rules"]["definitive_assignment_from_length_alone"])

    def test_length_only_mapping_not_definitive(self):
        with (LABELS / "LIFE_STAGE_MAPPING.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        length_row = next(r for r in rows if r["source_id"] == "generic_length_bin")
        self.assertEqual(length_row["normalized_life_stage"], "unknown")
        self.assertIn("forbidden", length_row["mapping_confidence"])

    def test_calcofi_is_egg_not_adult(self):
        with (LABELS / "LIFE_STAGE_MAPPING.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        cal = next(r for r in rows if r["source_id"] == "erdCalCOFIcufes")
        self.assertEqual(cal["normalized_life_stage"], "egg")


class ModelQuestionRouter(unittest.TestCase):
    def test_router_has_core_routes(self):
        router = yaml.safe_load(
            (SCIENCE / "MODEL_QUESTION_ROUTER.yaml").read_text(encoding="utf-8")
        )
        ids = {route["id"] for route in router["routes"]}
        for required in (
            "survey_with_valid_nondetections",
            "positive_counts_with_effort",
            "presence_only",
            "individual_ordered_tracks",
            "receiver_detections",
            "eggs_or_larvae_plus_currents",
            "nowcast_present_conditions",
            "forecast_future_days",
            "climate_future_periods",
        ):
            self.assertIn(required, ids)
        self.assertIn("generic classifier", router["hard_rule"].lower())


class NoCoordinatesInFixtures(unittest.TestCase):
    def test_synthetic_rows_have_no_lat_lon(self):
        row = base_valid_nondetection()
        for banned in ("latitude", "longitude", "lat", "lon", "coords"):
            self.assertNotIn(banned, row)


if __name__ == "__main__":
    unittest.main()
