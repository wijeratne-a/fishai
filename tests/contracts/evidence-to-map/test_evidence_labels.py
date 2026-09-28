"""Evidence-to-map label honesty — synthetic payloads only; no coordinates printed."""

from __future__ import annotations

import unittest
from typing import Any


FORBIDDEN_FISH_SIGHTING_LABELS = {
    "DIRECT_OBSERVATION",
    "STRUCTURED_SURVEY_DETECTION",
    "RECENT_PRESENCE_EVIDENCE",
}


def map_materialization_errors(payload: dict[str, Any]) -> list[str]:
    """
    Return rejection reasons for a proposed map/globe materialization.

    Empty list means the payload is not rejected by these honesty rules
    (it may still be schema-invalid elsewhere).
    """
    errors: list[str] = []
    label = payload.get("evidence_label") or payload.get("output_class")
    source_kind = payload.get("source_kind")
    publish_status = payload.get("publish_status")
    scientific_status = payload.get("scientific_status")
    claims = set(payload.get("claims") or [])

    # 1) SST is not a fish sighting
    if source_kind == "SST" or payload.get("measurement_type") == "sea_surface_temperature":
        if label in FORBIDDEN_FISH_SIGHTING_LABELS or "fish_sighting" in claims:
            errors.append("sst_is_not_a_fish_sighting")
        if label not in (None, "ENVIRONMENTAL_CONDITION", "UNKNOWN"):
            if label in FORBIDDEN_FISH_SIGHTING_LABELS:
                pass  # already recorded
            elif label != "ENVIRONMENTAL_CONDITION":
                errors.append("sst_must_use_environmental_condition_label")

    # 2) OBIS presence is not a current location
    if source_kind == "OBIS" or payload.get("presence_compiler") is True:
        if "current_location" in claims or scientific_status == "current_estimate":
            errors.append("obis_presence_is_not_current_location")
        if label in ("PUBLISHED_NOWCAST", "RECENT_PRESENCE_EVIDENCE") and "current_location" in claims:
            errors.append("obis_presence_is_not_current_location")

    # 3) Survey zero is not regional ecological absence
    if label == "SURVEY_NONDETECTION" or payload.get("observation_state") == "SURVEY_NONDETECTION":
        if payload.get("is_ecological_absence_claim") is True or "regional_ecological_absence" in claims:
            errors.append("survey_zero_is_not_regional_ecological_absence")

    # 4) Internal baseline is not a published nowcast
    if payload.get("is_internal_baseline") is True or label == "INTERNAL_MODEL_OUTPUT":
        if label == "PUBLISHED_NOWCAST" or "published_nowcast" in claims:
            errors.append("internal_baseline_is_not_published_nowcast")
        if publish_status in (None, "NOT_PUBLISHED", "INTERNAL_ONLY") and label == "PUBLISHED_NOWCAST":
            errors.append("internal_baseline_is_not_published_nowcast")

    # 5) Forecast requires issue time and valid window
    if label == "PUBLISHED_FORECAST" or scientific_status == "forecast":
        if not payload.get("issued_at_utc"):
            errors.append("forecast_requires_issued_at_utc")
        if not payload.get("valid_from_utc"):
            errors.append("forecast_requires_valid_from_utc")
        if not payload.get("valid_to_utc"):
            errors.append("forecast_requires_valid_to_utc")

    # 6) NOT_PUBLISHED must not produce a probability layer on the map
    if publish_status == "NOT_PUBLISHED":
        if payload.get("produces_probability_layer") is True or "probability_layer" in claims:
            errors.append("not_published_cannot_produce_probability_layer")
        if label in ("PUBLISHED_NOWCAST", "PUBLISHED_FORECAST"):
            errors.append("not_published_cannot_produce_probability_layer")

    return sorted(set(errors))


class EvidenceToMapLabelTests(unittest.TestCase):
    def test_rejects_sst_as_fish_sighting(self):
        payload = {
            "source_kind": "SST",
            "measurement_type": "sea_surface_temperature",
            "evidence_label": "DIRECT_OBSERVATION",
            "claims": ["fish_sighting"],
        }
        errors = map_materialization_errors(payload)
        self.assertIn("sst_is_not_a_fish_sighting", errors)

    def test_accepts_sst_as_environmental_condition(self):
        payload = {
            "source_kind": "SST",
            "measurement_type": "sea_surface_temperature",
            "evidence_label": "ENVIRONMENTAL_CONDITION",
            "claims": [],
        }
        self.assertEqual(map_materialization_errors(payload), [])

    def test_rejects_obis_presence_as_current_location(self):
        payload = {
            "source_kind": "OBIS",
            "presence_compiler": True,
            "evidence_label": "HISTORICAL_OCCURRENCE",
            "scientific_status": "current_estimate",
            "claims": ["current_location"],
        }
        errors = map_materialization_errors(payload)
        self.assertIn("obis_presence_is_not_current_location", errors)

    def test_rejects_survey_zero_as_regional_absence(self):
        payload = {
            "evidence_label": "SURVEY_NONDETECTION",
            "observation_state": "SURVEY_NONDETECTION",
            "is_ecological_absence_claim": True,
            "claims": ["regional_ecological_absence"],
        }
        errors = map_materialization_errors(payload)
        self.assertIn("survey_zero_is_not_regional_ecological_absence", errors)

    def test_rejects_internal_baseline_as_published_nowcast(self):
        payload = {
            "is_internal_baseline": True,
            "publish_status": "NOT_PUBLISHED",
            "evidence_label": "PUBLISHED_NOWCAST",
            "output_class": "PUBLISHED_NOWCAST",
            "claims": ["published_nowcast"],
        }
        errors = map_materialization_errors(payload)
        self.assertIn("internal_baseline_is_not_published_nowcast", errors)

    def test_rejects_forecast_without_issue_and_valid_times(self):
        payload = {
            "evidence_label": "PUBLISHED_FORECAST",
            "scientific_status": "forecast",
            "publish_status": "PUBLISHED",
            "issued_at_utc": None,
            "valid_from_utc": None,
            "valid_to_utc": None,
        }
        errors = map_materialization_errors(payload)
        self.assertIn("forecast_requires_issued_at_utc", errors)
        self.assertIn("forecast_requires_valid_from_utc", errors)
        self.assertIn("forecast_requires_valid_to_utc", errors)

    def test_accepts_forecast_with_issue_and_valid_times(self):
        payload = {
            "evidence_label": "PUBLISHED_FORECAST",
            "scientific_status": "forecast",
            "publish_status": "PUBLISHED",
            "issued_at_utc": "2026-09-24T00:00:00Z",
            "valid_from_utc": "2026-09-24T00:00:00Z",
            "valid_to_utc": "2026-09-25T00:00:00Z",
        }
        self.assertEqual(map_materialization_errors(payload), [])

    def test_rejects_not_published_probability_layer(self):
        payload = {
            "publish_status": "NOT_PUBLISHED",
            "output_class": "INTERNAL_MODEL_OUTPUT",
            "evidence_label": "INTERNAL_MODEL_OUTPUT",
            "produces_probability_layer": True,
            "claims": ["probability_layer"],
        }
        errors = map_materialization_errors(payload)
        self.assertIn("not_published_cannot_produce_probability_layer", errors)


if __name__ == "__main__":
    unittest.main()
