"""WS measurements unit validation — synthetic values only; no raw survey joins."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCIENCE = REPO_ROOT / "science" / "measurements"
AUDIT = REPO_ROOT / "audit" / "measurements"


def load_registry() -> dict:
    with (SCIENCE / "UNIT_REGISTRY.yaml").open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_conflicts() -> list[dict]:
    with (AUDIT / "UNIT_CONFLICTS.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_measurement(row: dict, registry: dict | None = None) -> list[str]:
    """Return conflict ids for forbidden unit/quantity patterns; empty means accept."""
    registry = registry or load_registry()
    errors: list[str] = []
    forbidden = {item["conflict_id"]: item for item in registry["forbidden_equivalences"]}
    time_rules = registry["time_precision_rules"]

    declared_unit = row.get("measurement_unit")
    native_unit = row.get("measurement_unit_native")
    mtype = row.get("measurement_type")
    quantity = row.get("quantity")
    treatment = row.get("treatment")
    value = row.get("measurement_value")
    converted = row.get("explicit_conversion") is True

    # Feet labeled as meters without conversion
    if native_unit == "foot" and declared_unit == "meter" and not converted:
        errors.append(forbidden["UC-LENGTH-FT-AS-M"]["conflict_id"])
    if (
        row.get("unit_claim") == "meter"
        and row.get("value_actually_in") == "foot"
        and not converted
    ):
        if "UC-LENGTH-FT-AS-M" not in errors:
            errors.append("UC-LENGTH-FT-AS-M")

    # Kelvin labeled as Celsius without conversion
    if native_unit == "kelvin" and declared_unit == "degree_celsius" and not converted:
        errors.append("UC-TEMP-K-AS-C")
    if (
        row.get("unit_claim") == "degree_celsius"
        and row.get("value_actually_in") == "kelvin"
        and not converted
    ):
        if "UC-TEMP-K-AS-C" not in errors:
            errors.append("UC-TEMP-K-AS-C")

    # Atlantic RVC NUM average treated as integer fish count
    if mtype == "atlantic_rvc_num" or quantity == "real_valued_average":
        if treatment in {"integer_fish_count", "integer_count"} or row.get(
            "treated_as_integer_fish_count"
        ):
            errors.append("UC-NUM-AS-INTEGER-COUNT")
        if declared_unit == "count" and quantity == "real_valued_average":
            errors.append("UC-NUM-AS-INTEGER-COUNT")
        if isinstance(value, float) and row.get("cast_to_int_fish_count") is True:
            errors.append("UC-NUM-AS-INTEGER-COUNT")

    # Count as density
    if quantity == "count" and (
        treatment == "density"
        or declared_unit in {"density", "1/m2"}
        or row.get("labeled_as") == "density"
    ):
        if row.get("area_denominator") in (None, "", 0):
            errors.append("UC-COUNT-AS-DENSITY")

    # CPUE as abundance
    if quantity == "cpue" and (
        treatment == "abundance"
        or row.get("labeled_as") == "abundance"
        or declared_unit == "abundance"
    ):
        if row.get("effort_expansion_documented") is not True:
            errors.append("UC-CPUE-AS-ABUNDANCE")

    # SST labeled as bottom temperature
    if mtype == "sea_surface_temperature" and row.get("labeled_as") == "bottom_temperature":
        errors.append("UC-SST-AS-BOTTOM-TEMP")
    if (
        row.get("source_product") == "analysed_sst"
        and mtype == "bottom_temperature"
        and row.get("depth_resolved_product") is not True
    ):
        errors.append("UC-SST-AS-BOTTOM-TEMP")

    # Date-only given an invented hour
    if row.get("time_precision") == "DAY" or row.get("source_precision") == "DAY":
        if row.get("invented_hour") is True or row.get("fabricated_clock") is True:
            errors.append(time_rules["date_only"]["conflict_id"])
        observed = row.get("observed_at_utc")
        if isinstance(observed, str) and "T" in observed and row.get("date_only_source") is True:
            errors.append(time_rules["date_only"]["conflict_id"])

    return sorted(set(errors))


class UnitRegistryTests(unittest.TestCase):
    def test_registry_and_conflicts_exist(self) -> None:
        registry = load_registry()
        self.assertIn("forbidden_equivalences", registry)
        conflicts = load_conflicts()
        ids = {row["conflict_id"] for row in conflicts}
        for conflict_id in (
            "UC-LENGTH-FT-AS-M",
            "UC-TEMP-K-AS-C",
            "UC-NUM-AS-INTEGER-COUNT",
            "UC-COUNT-AS-DENSITY",
            "UC-CPUE-AS-ABUNDANCE",
            "UC-SST-AS-BOTTOM-TEMP",
            "UC-DATE-ONLY-INVENTED-HOUR",
        ):
            self.assertIn(conflict_id, ids)

    def test_semantics_document_num_real_valued_average(self) -> None:
        text = (SCIENCE / "MEASUREMENT_SEMANTICS.md").read_text(encoding="utf-8")
        self.assertIn("real-valued average", text)
        self.assertIn("not an integer fish count", text)
        self.assertIn("ATLANTIC_ZERO_SEMANTICS.md", text)


class ForbiddenUnitPatternsFail(unittest.TestCase):
    """Each case must produce a non-empty conflict list (validation failure)."""

    def test_feet_as_meters_fails(self) -> None:
        row = {
            "measurement_type": "depth",
            "measurement_value": 30.0,  # synthetic feet
            "measurement_unit_native": "foot",
            "measurement_unit": "meter",
            "explicit_conversion": False,
        }
        errors = validate_measurement(row)
        self.assertIn("UC-LENGTH-FT-AS-M", errors)

    def test_kelvin_as_celsius_fails(self) -> None:
        row = {
            "measurement_type": "sea_surface_temperature",
            "measurement_value": 300.15,  # synthetic Kelvin
            "measurement_unit_native": "kelvin",
            "measurement_unit": "degree_celsius",
            "explicit_conversion": False,
        }
        errors = validate_measurement(row)
        self.assertIn("UC-TEMP-K-AS-C", errors)

    def test_num_average_as_integer_fish_count_fails(self) -> None:
        row = {
            "measurement_type": "atlantic_rvc_num",
            "quantity": "real_valued_average",
            "measurement_value": 2.35,  # synthetic average
            "measurement_unit": "real_valued_average",
            "treated_as_integer_fish_count": True,
            "cast_to_int_fish_count": True,
        }
        errors = validate_measurement(row)
        self.assertIn("UC-NUM-AS-INTEGER-COUNT", errors)

    def test_count_as_density_fails(self) -> None:
        row = {
            "measurement_type": "survey_count",
            "quantity": "count",
            "measurement_value": 7,  # synthetic count
            "measurement_unit": "count",
            "labeled_as": "density",
            "area_denominator": None,
        }
        errors = validate_measurement(row)
        self.assertIn("UC-COUNT-AS-DENSITY", errors)

    def test_cpue_as_abundance_fails(self) -> None:
        row = {
            "measurement_type": "cpue_index",
            "quantity": "cpue",
            "measurement_value": 1.2,  # synthetic CPUE
            "measurement_unit": "cpue",
            "labeled_as": "abundance",
            "effort_expansion_documented": False,
        }
        errors = validate_measurement(row)
        self.assertIn("UC-CPUE-AS-ABUNDANCE", errors)

    def test_sst_labeled_as_bottom_temperature_fails(self) -> None:
        row = {
            "measurement_type": "sea_surface_temperature",
            "quantity": "sea_surface_temperature",
            "measurement_value": 27.4,  # synthetic degC
            "measurement_unit": "degree_celsius",
            "labeled_as": "bottom_temperature",
            "source_product": "analysed_sst",
        }
        errors = validate_measurement(row)
        self.assertIn("UC-SST-AS-BOTTOM-TEMP", errors)

    def test_date_only_invented_hour_fails(self) -> None:
        row = {
            "measurement_type": "atlantic_rvc_num",
            "quantity": "real_valued_average",
            "measurement_value": 0.0,
            "measurement_unit": "real_valued_average",
            "time_precision": "DAY",
            "date_only_source": True,
            "invented_hour": True,
            "observed_at_utc": "2022-06-15T12:00:00Z",  # fabricated clock
        }
        errors = validate_measurement(row)
        self.assertIn("UC-DATE-ONLY-INVENTED-HOUR", errors)


class AllowedPatternsPass(unittest.TestCase):
    def test_converted_feet_to_meters_ok(self) -> None:
        row = {
            "measurement_type": "depth",
            "measurement_value": 9.144,
            "measurement_unit_native": "foot",
            "measurement_unit": "meter",
            "explicit_conversion": True,
        }
        self.assertEqual(validate_measurement(row), [])

    def test_num_kept_as_real_valued_average_ok(self) -> None:
        row = {
            "measurement_type": "atlantic_rvc_num",
            "quantity": "real_valued_average",
            "measurement_value": 2.35,
            "measurement_unit": "real_valued_average",
            "treated_as_integer_fish_count": False,
        }
        self.assertEqual(validate_measurement(row), [])


if __name__ == "__main__":
    unittest.main()
