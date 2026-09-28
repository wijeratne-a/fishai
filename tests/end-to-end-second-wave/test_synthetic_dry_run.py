"""SYNTHETIC TEST DATA — second-wave end-to-end dry run.

No real survey files. No coordinates in outputs.
No missing-to-absence. No internal-to-published promotion.
"""

from __future__ import annotations

import unittest
from typing import Any

# Label every payload so dumps/logs cannot be mistaken for production rows.
DATASET_LABEL = "SYNTHETIC TEST DATA"

FORBIDDEN_COORD_KEYS = frozenset(
    {"latitude", "longitude", "lat", "lon", "lng", "coord", "geometry"}
)


def label_event(
    event: dict[str, Any],
    species_code: str,
    *,
    frame_codes: set[str] | None,
) -> dict[str, Any]:
    """Label one species. Missing code without frame membership → NOT_EVALUATED."""
    base = {
        "dataset_label": DATASET_LABEL,
        "event_id": event["event_id"],
        "species_code": species_code,
    }
    if not event.get("effort_completed"):
        return {**base, "label": "NOT_EVALUATED", "reason": "effort_incomplete"}

    if frame_codes is None or species_code not in frame_codes:
        return {
            **base,
            "label": "NOT_EVALUATED",
            "reason": "missing_not_absence",
        }

    counts = event.get("counts", {})
    if species_code not in counts:
        # On-frame but row missing → still not an invented zero.
        return {
            **base,
            "label": "NOT_EVALUATED",
            "reason": "on_frame_row_missing",
        }

    value = counts[species_code]
    if value > 0:
        return {**base, "label": "DETECTION", "count": value}
    if value == 0:
        return {**base, "label": "SURVEY_NONDETECTION", "count": 0}
    return {**base, "label": "NOT_EVALUATED", "reason": "invalid_count"}


def build_internal_output(
    *,
    species_code: str,
    label: str,
    support: str,
) -> dict[str, Any]:
    return {
        "dataset_label": DATASET_LABEL,
        "species_code": species_code,
        "label": label,
        "support": support,
        "output_class": "INTERNAL_MODEL_OUTPUT",
        "spatial_cell_id": "SYNTHETIC_CELL_B",
    }


def promote_to_published(internal: dict[str, Any]) -> dict[str, Any]:
    """Promotion is forbidden; return WITHHELD instead of PUBLISHED_*."""
    return {
        "dataset_label": DATASET_LABEL,
        "species_code": internal["species_code"],
        "output_class": "WITHHELD",
        "reason": "internal_to_published_forbidden",
        "source_output_class": internal.get("output_class"),
    }


def _assert_no_coordinates(payload: dict[str, Any]) -> None:
    for key in payload:
        if key.lower() in FORBIDDEN_COORD_KEYS:
            raise AssertionError(f"coordinate field forbidden: {key}")
        val = payload[key]
        if isinstance(val, dict):
            _assert_no_coordinates(val)


class SyntheticSecondWaveDryRunTest(unittest.TestCase):
    def test_dataset_is_labeled_synthetic(self):
        self.assertEqual(DATASET_LABEL, "SYNTHETIC TEST DATA")

    def test_explicit_zero_is_nondetection(self):
        event = {
            "event_id": "SYN-E1",
            "effort_completed": True,
            "counts": {"SP_A": 0},
        }
        out = label_event(event, "SP_A", frame_codes={"SP_A", "SP_B"})
        self.assertEqual(out["label"], "SURVEY_NONDETECTION")
        self.assertEqual(out["dataset_label"], DATASET_LABEL)
        _assert_no_coordinates(out)

    def test_missing_is_not_absence(self):
        event = {
            "event_id": "SYN-E2",
            "effort_completed": True,
            "counts": {"SP_A": 1},
        }
        # Species not on frame → must not become SURVEY_NONDETECTION / absence.
        out = label_event(event, "SP_MISSING", frame_codes=None)
        self.assertEqual(out["label"], "NOT_EVALUATED")
        self.assertEqual(out["reason"], "missing_not_absence")
        self.assertNotEqual(out["label"], "SURVEY_NONDETECTION")
        self.assertNotIn("absence", out.get("label", "").lower())

    def test_no_coordinates_in_outputs(self):
        internal = build_internal_output(
            species_code="SP_A",
            label="SURVEY_NONDETECTION",
            support="SUPPORTED",
        )
        _assert_no_coordinates(internal)
        published = promote_to_published(internal)
        _assert_no_coordinates(published)

    def test_no_internal_to_published_promotion(self):
        internal = build_internal_output(
            species_code="SP_A",
            label="DETECTION",
            support="SUPPORTED",
        )
        self.assertEqual(internal["output_class"], "INTERNAL_MODEL_OUTPUT")
        gated = promote_to_published(internal)
        self.assertEqual(gated["output_class"], "WITHHELD")
        self.assertNotIn("PUBLISHED", gated["output_class"])
        self.assertEqual(gated["reason"], "internal_to_published_forbidden")

    def test_end_to_end_synthetic_chain(self):
        event = {
            "event_id": "SYN-E3",
            "effort_completed": True,
            "counts": {"SP_A": 0},
        }
        labeled = label_event(event, "SP_A", frame_codes={"SP_A"})
        self.assertEqual(labeled["label"], "SURVEY_NONDETECTION")
        self.assertEqual(labeled["dataset_label"], DATASET_LABEL)

        missing = label_event(event, "SP_Z", frame_codes={"SP_A"})
        self.assertEqual(missing["label"], "NOT_EVALUATED")

        internal = build_internal_output(
            species_code="SP_A",
            label=labeled["label"],
            support="SUPPORTED",
        )
        _assert_no_coordinates(internal)
        gated = promote_to_published(internal)
        self.assertEqual(gated["output_class"], "WITHHELD")
        _assert_no_coordinates(gated)


if __name__ == "__main__":
    unittest.main()
