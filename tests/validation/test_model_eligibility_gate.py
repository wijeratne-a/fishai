"""A bad file must be rejected and quarantined. data/raw is never edited."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "validation"))

from model_eligibility import gate_file  # noqa: E402

RAW = REPO_ROOT / "data" / "raw"
QUARANTINE = REPO_ROOT / "data" / "quarantine"


def _write_bad_atlantic(path: Path) -> None:
    """Synthetic frame: mixed zero and positive on the same species-event."""
    fields = [
        "time",
        "YEAR",
        "MONTH",
        "DAY",
        "PRIMARY_SAMPLE_UNIT",
        "STATION_NR",
        "SAMPLE_DEPTH",
        "HABITAT_CD",
        "SPECIES_CD",
        "NUM",
    ]
    rows = [
        {
            "time": "2021-06-01T00:00:00Z",
            "YEAR": "2021",
            "MONTH": "6",
            "DAY": "1",
            "PRIMARY_SAMPLE_UNIT": "SYN1",
            "STATION_NR": "1",
            "SAMPLE_DEPTH": "10",
            "HABITAT_CD": "HR",
            "SPECIES_CD": "STE PART",
            "NUM": "0",
        },
        {
            "time": "2021-06-01T00:00:00Z",
            "YEAR": "2021",
            "MONTH": "6",
            "DAY": "1",
            "PRIMARY_SAMPLE_UNIT": "SYN1",
            "STATION_NR": "1",
            "SAMPLE_DEPTH": "10",
            "HABITAT_CD": "HR",
            "SPECIES_CD": "STE PART",
            "NUM": "2.35",
        },
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class ModelEligibilityGateTests(unittest.TestCase):
    def test_bad_file_is_rejected_and_quarantined(self) -> None:
        raw_before = set()
        if RAW.exists():
            raw_before = {p.name for p in RAW.rglob("*") if p.is_file()}

        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "synthetic-bad-atlantic.csv"
            _write_bad_atlantic(bad)
            result = gate_file(
                bad,
                dataset_id="SYNTHETIC_BAD_ATLANTIC",
                family="atlantic",
                sidecar={"license_class": "AUTO_ACQUIRE_INTERNAL_ONLY"},
                quarantine=True,
            )
        self.assertEqual(result["status"], "REJECTED")
        self.assertTrue(result["errors"])
        self.assertIn("MIXED_ZERO_AND_POSITIVE_ON_SAME_SPECIES_EVENT", result["errors"])
        self.assertIsNotNone(result["quarantine_path"])
        self.assertTrue(Path(result["quarantine_path"]).is_file())
        self.assertFalse(result["raw_edited"])

        if RAW.exists():
            raw_after = {p.name for p in RAW.rglob("*") if p.is_file()}
            self.assertEqual(raw_before, raw_after)

    def test_num_as_integer_count_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic-num-as-count.csv"
            _write_goodish(path)
            result = gate_file(
                path,
                dataset_id="SYNTHETIC_NUM",
                family="atlantic",
                sidecar={
                    "license_class": "AUTO_ACQUIRE_INTERNAL_ONLY",
                    "treated_as_integer_fish_count": True,
                    "measurement_type": "atlantic_rvc_num",
                    "treatment": "integer_fish_count",
                },
                quarantine=True,
            )
        self.assertEqual(result["status"], "REJECTED")
        self.assertIn("UC-NUM-AS-INTEGER-COUNT", result["errors"])

    def test_unknown_license_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic-nolicense.csv"
            _write_goodish(path)
            result = gate_file(
                path,
                dataset_id="SYNTHETIC_NOLICENSE",
                family="atlantic",
                sidecar={},
                quarantine=True,
            )
        self.assertEqual(result["status"], "REJECTED")
        self.assertIn("LICENSE_CLASS_UNKNOWN", result["errors"])


def _write_goodish(path: Path) -> None:
    fields = [
        "time",
        "YEAR",
        "MONTH",
        "DAY",
        "PRIMARY_SAMPLE_UNIT",
        "STATION_NR",
        "SAMPLE_DEPTH",
        "HABITAT_CD",
        "SPECIES_CD",
        "NUM",
    ]
    rows = [
        {
            "time": "2021-06-01T00:00:00Z",
            "YEAR": "2021",
            "MONTH": "6",
            "DAY": "1",
            "PRIMARY_SAMPLE_UNIT": "SYN1",
            "STATION_NR": "1",
            "SAMPLE_DEPTH": "10",
            "HABITAT_CD": "HR",
            "SPECIES_CD": "STE PART",
            "NUM": "0",
        },
        {
            "time": "2021-06-01T00:00:00Z",
            "YEAR": "2021",
            "MONTH": "6",
            "DAY": "1",
            "PRIMARY_SAMPLE_UNIT": "SYN1",
            "STATION_NR": "1",
            "SAMPLE_DEPTH": "10",
            "HABITAT_CD": "HR",
            "SPECIES_CD": "SPA AURO",
            "NUM": "1.5",
        },
        {
            "time": "2021-06-02T00:00:00Z",
            "YEAR": "2021",
            "MONTH": "6",
            "DAY": "2",
            "PRIMARY_SAMPLE_UNIT": "SYN2",
            "STATION_NR": "1",
            "SAMPLE_DEPTH": "12",
            "HABITAT_CD": "HR",
            "SPECIES_CD": "STE PART",
            "NUM": "0",
        },
        {
            "time": "2021-06-02T00:00:00Z",
            "YEAR": "2021",
            "MONTH": "6",
            "DAY": "2",
            "PRIMARY_SAMPLE_UNIT": "SYN2",
            "STATION_NR": "1",
            "SAMPLE_DEPTH": "12",
            "HABITAT_CD": "HR",
            "SPECIES_CD": "SPA AURO",
            "NUM": "0",
        },
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
