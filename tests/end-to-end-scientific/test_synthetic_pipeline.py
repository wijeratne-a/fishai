"""End-to-end scientific pipeline checks using synthetic rows only.

No real survey files, coordinates, or live globe wiring.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from typing import Any


# --- Synthetic pipeline (test-local; not production labels/) -----------------


FORBIDDEN_COORD_KEYS = frozenset({"latitude", "longitude", "lat", "lon", "lng"})


def label_survey_event(
    event: dict[str, Any],
    species_code: str,
    *,
    frame_codes: set[str] | None,
) -> dict[str, Any]:
    """Label one species on a survey event.

    Explicit zero on a completed event whose frame includes the code → non-detection.
    Species absent from the frame (or no frame) → NOT_EVALUATED.
    """
    if not event.get("effort_completed"):
        return {
            "event_id": event["event_id"],
            "species_code": species_code,
            "label": "NOT_EVALUATED",
            "reason": "effort_incomplete",
        }

    if frame_codes is None or species_code not in frame_codes:
        return {
            "event_id": event["event_id"],
            "species_code": species_code,
            "label": "NOT_EVALUATED",
            "reason": "missing_species_without_frame",
        }

    counts = event.get("counts", {})
    if species_code not in counts:
        return {
            "event_id": event["event_id"],
            "species_code": species_code,
            "label": "NOT_EVALUATED",
            "reason": "code_not_on_event",
        }

    value = counts[species_code]
    if value > 0:
        label = "DETECTION"
    elif value == 0:
        label = "SURVEY_NONDETECTION"
    else:
        return {
            "event_id": event["event_id"],
            "species_code": species_code,
            "label": "NOT_EVALUATED",
            "reason": "invalid_count",
        }

    return {
        "event_id": event["event_id"],
        "species_code": species_code,
        "label": label,
        "count": value,
    }


def join_feature(
    event_time: datetime,
    covariate_time: datetime,
    value: float,
) -> dict[str, Any] | None:
    """Attach a covariate only when it is not from the future relative to the event."""
    if covariate_time > event_time:
        return None
    return {"value": value, "covariate_time": covariate_time.isoformat()}


def apply_support_mask(
    value: float,
    *,
    vmin: float,
    vmax: float,
) -> str:
    """Mark out-of-range covariates UNSUPPORTED; in-range SUPPORT."""
    if value < vmin or value > vmax:
        return "UNSUPPORTED"
    return "SUPPORTED"


def build_internal_output(
    *,
    species_code: str,
    probability: float,
    support: str,
    valid_time: str,
    model_version: str,
) -> dict[str, Any]:
    """Internal model payload: INTERNAL label, no coordinate fields."""
    return {
        "species_code": species_code,
        "output_class": "INTERNAL",
        "probability": probability,
        "support": support,
        "valid_time": valid_time,
        "model_version": model_version,
        "spatial_cell_id": "SYNTHETIC_CELL_A",
    }


def _assert_no_coordinates(payload: dict[str, Any]) -> None:
    keys_lower = {k.lower() for k in payload}
    overlap = keys_lower & {k.lower() for k in FORBIDDEN_COORD_KEYS}
    if overlap:
        raise AssertionError(f"coordinate fields forbidden: {sorted(overlap)}")


# --- Tests -------------------------------------------------------------------


class SyntheticPipelineTest(unittest.TestCase):
    def test_explicit_zero_is_nondetection(self):
        event = {
            "event_id": "E1",
            "effort_completed": True,
            "counts": {"SP_A": 0},
        }
        frame = {"SP_A", "SP_B"}
        labeled = label_survey_event(event, "SP_A", frame_codes=frame)
        self.assertEqual(labeled["label"], "SURVEY_NONDETECTION")
        self.assertEqual(labeled["count"], 0)

    def test_missing_species_without_frame_stays_not_evaluated(self):
        event = {
            "event_id": "E2",
            "effort_completed": True,
            "counts": {"SP_A": 1},
        }
        labeled = label_survey_event(event, "SP_MISSING", frame_codes=None)
        self.assertEqual(labeled["label"], "NOT_EVALUATED")
        self.assertEqual(labeled["reason"], "missing_species_without_frame")

        labeled_empty_frame = label_survey_event(
            event, "SP_MISSING", frame_codes=set()
        )
        self.assertEqual(labeled_empty_frame["label"], "NOT_EVALUATED")

    def test_features_reject_future_covariate(self):
        event_time = datetime(2023, 6, 1, 12, 0, tzinfo=timezone.utc)
        future = datetime(2023, 6, 2, 0, 0, tzinfo=timezone.utc)
        past = datetime(2023, 5, 31, 18, 0, tzinfo=timezone.utc)

        self.assertIsNone(join_feature(event_time, future, 24.0))
        joined = join_feature(event_time, past, 24.0)
        self.assertIsNotNone(joined)
        assert joined is not None
        self.assertEqual(joined["value"], 24.0)

    def test_support_mask_marks_out_of_range_unsupported(self):
        self.assertEqual(apply_support_mask(30.0, vmin=20.0, vmax=28.0), "UNSUPPORTED")
        self.assertEqual(apply_support_mask(24.0, vmin=20.0, vmax=28.0), "SUPPORTED")

    def test_output_is_internal_without_coordinates(self):
        out = build_internal_output(
            species_code="SP_A",
            probability=0.22,
            support="SUPPORTED",
            valid_time="2023-06-01T12:00:00Z",
            model_version="synthetic-internal-v0",
        )
        self.assertEqual(out["output_class"], "INTERNAL")
        self.assertNotIn("PUBLISHED", str(out["output_class"]))
        _assert_no_coordinates(out)
        self.assertNotIn("latitude", out)
        self.assertNotIn("longitude", out)

    def test_end_to_end_synthetic_chain(self):
        """Label → non-future feature → support mask → INTERNAL output."""
        event = {
            "event_id": "E3",
            "effort_completed": True,
            "counts": {"SP_A": 0},
            "observed_at": datetime(2023, 6, 1, 12, 0, tzinfo=timezone.utc),
        }
        frame = {"SP_A"}
        labeled = label_survey_event(event, "SP_A", frame_codes=frame)
        self.assertEqual(labeled["label"], "SURVEY_NONDETECTION")

        feature = join_feature(
            event["observed_at"],
            datetime(2023, 6, 1, 6, 0, tzinfo=timezone.utc),
            29.5,
        )
        self.assertIsNotNone(feature)
        assert feature is not None

        support = apply_support_mask(feature["value"], vmin=20.0, vmax=28.0)
        self.assertEqual(support, "UNSUPPORTED")

        # Species not in any frame stays unevaluated (separate branch).
        missing = label_survey_event(event, "SP_Z", frame_codes=None)
        self.assertEqual(missing["label"], "NOT_EVALUATED")

        out = build_internal_output(
            species_code="SP_A",
            probability=0.0,
            support=support,
            valid_time="2023-06-01T12:00:00Z",
            model_version="synthetic-internal-v0",
        )
        self.assertEqual(out["output_class"], "INTERNAL")
        _assert_no_coordinates(out)


if __name__ == "__main__":
    unittest.main()
