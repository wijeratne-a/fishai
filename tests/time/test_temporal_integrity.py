"""WS time temporal integrity — synthetic timestamps only; no live forecast grids."""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCIENCE = REPO_ROOT / "science" / "time"


def load_forecast_schema() -> dict:
    with (SCIENCE / "FORECAST_TIME_SCHEMA.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def _parse_utc(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = value.replace("Z", "+00:00")
    return datetime.fromisoformat(text).astimezone(timezone.utc)


def validate_temporal_record(row: dict) -> list[str]:
    """Return integrity violation codes; empty means accept."""
    errors: list[str] = []
    lane = row.get("lane", "operational")

    event_time = _parse_utc(row.get("event_time_utc"))
    feature_available = _parse_utc(row.get("feature_available_at_utc"))
    feature_valid = _parse_utc(row.get("feature_valid_time_utc"))

    # Post-event values must not enter operational features
    if lane != "retrospective" and event_time is not None:
        if feature_available is not None and feature_available > event_time:
            errors.append("TI-POST-EVENT-FEATURE")
        elif (
            feature_available is None
            and feature_valid is not None
            and feature_valid > event_time
            and row.get("treat_valid_as_available") is True
        ):
            errors.append("TI-POST-EVENT-FEATURE")

    # Centered windows are not operational lags
    if row.get("window_kind") == "centered" and row.get("used_as") in {
        "operational_lag",
        "as_of_feature",
        "feature",
    }:
        if lane != "retrospective":
            errors.append("TI-CENTERED-WINDOW-AS-OPERATIONAL-LAG")

    # Forecast valid time equals issue time without a lead
    if row.get("product_kind") == "forecast":
        issue = _parse_utc(row.get("issue_time_utc"))
        valid = _parse_utc(row.get("valid_time_utc"))
        lead = row.get("lead_time")
        lead_hours = row.get("lead_time_hours")
        has_explicit_lead = lead is not None or lead_hours is not None
        if issue is not None and valid is not None and issue == valid and not has_explicit_lead:
            errors.append("TI-FORECAST-NO-LEAD")

    # Date-only record with fabricated timestamp
    if row.get("time_precision") == "DAY" or row.get("source_precision") == "DAY":
        if row.get("fabricated_clock") is True or row.get("invented_timestamp") is True:
            errors.append("TI-DATE-ONLY-FABRICATED-TIMESTAMP")
        stamp = row.get("observed_at_utc") or row.get("event_time_utc")
        if (
            isinstance(stamp, str)
            and "T" in stamp
            and row.get("date_only_source") is True
            and row.get("clock_from_source") is not True
        ):
            errors.append("TI-DATE-ONLY-FABRICATED-TIMESTAMP")

    return sorted(set(errors))


class TemporalContractFiles(unittest.TestCase):
    def test_rules_and_schema_exist(self) -> None:
        rules = (SCIENCE / "TEMPORAL_INTEGRITY_RULES.md").read_text(encoding="utf-8")
        self.assertIn("Post-event", rules)
        self.assertIn("Centered windows", rules)
        schema = load_forecast_schema()
        self.assertEqual(schema["title"], "ForecastTimeRecord")
        for field in ("issue_time_utc", "valid_time_utc", "lead_time", "time_precision"):
            self.assertIn(field, schema["properties"])


class ForbiddenTemporalPatternsFail(unittest.TestCase):
    def test_post_event_values_in_features_fails(self) -> None:
        row = {
            "lane": "operational",
            "event_time_utc": "2022-06-15T00:00:00Z",
            "feature_valid_time_utc": "2022-06-16T00:00:00Z",
            "feature_available_at_utc": "2022-06-17T12:00:00Z",  # after event
            "feature_name": "synthetic_sst",
        }
        errors = validate_temporal_record(row)
        self.assertIn("TI-POST-EVENT-FEATURE", errors)

    def test_centered_window_as_operational_lag_fails(self) -> None:
        row = {
            "lane": "operational",
            "event_time_utc": "2022-06-15T00:00:00Z",
            "window_kind": "centered",
            "window_days": 7,  # synthetic ±7d
            "used_as": "operational_lag",
        }
        errors = validate_temporal_record(row)
        self.assertIn("TI-CENTERED-WINDOW-AS-OPERATIONAL-LAG", errors)

    def test_forecast_valid_equals_issue_without_lead_fails(self) -> None:
        row = {
            "record_id": "syn-fcst-1",
            "product_kind": "forecast",
            "issue_time_utc": "2022-06-15T00:00:00Z",
            "valid_time_utc": "2022-06-15T00:00:00Z",
            "lead_time": None,
            "lead_time_hours": None,
            "time_precision": "HOUR",
        }
        errors = validate_temporal_record(row)
        self.assertIn("TI-FORECAST-NO-LEAD", errors)

    def test_date_only_fabricated_timestamp_fails(self) -> None:
        row = {
            "time_precision": "DAY",
            "date_only_source": True,
            "fabricated_clock": True,
            "observed_at_utc": "2018-07-04T12:00:00Z",
            "event_time_utc": "2018-07-04T12:00:00Z",
        }
        errors = validate_temporal_record(row)
        self.assertIn("TI-DATE-ONLY-FABRICATED-TIMESTAMP", errors)


class AllowedTemporalPatternsPass(unittest.TestCase):
    def test_pre_event_feature_ok(self) -> None:
        row = {
            "lane": "operational",
            "event_time_utc": "2022-06-15T00:00:00Z",
            "feature_valid_time_utc": "2022-06-14T00:00:00Z",
            "feature_available_at_utc": "2022-06-14T18:00:00Z",
        }
        self.assertEqual(validate_temporal_record(row), [])

    def test_forecast_with_explicit_zero_lead_ok(self) -> None:
        row = {
            "product_kind": "forecast",
            "issue_time_utc": "2022-06-15T00:00:00Z",
            "valid_time_utc": "2022-06-15T00:00:00Z",
            "lead_time": "PT0H",
            "lead_time_hours": 0,
            "time_precision": "HOUR",
            "lane": "operational",
        }
        self.assertEqual(validate_temporal_record(row), [])

    def test_date_only_without_clock_ok(self) -> None:
        row = {
            "time_precision": "DAY",
            "date_only_source": True,
            "fabricated_clock": False,
            "observed_at_utc": "2018-07-04",
            "event_time_utc": "2018-07-04T00:00:00Z",
            "clock_from_source": False,
            # day-start sentinel allowed only when not marked fabricated and
            # date_only path uses date string for observed_at; event day-start
            # without fabricated_clock flag is accepted for storage anchors.
        }
        # observed_at is date-only (no T) so no fabrication error
        self.assertEqual(validate_temporal_record(row), [])


if __name__ == "__main__":
    unittest.main()
