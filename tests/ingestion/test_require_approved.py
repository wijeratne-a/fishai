"""Tests for data/SOURCES.yaml ingestion guard."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from fishai.ingestion.sources import (
    SourceNotApprovedError,
    attribution_for,
    require_approved,
)


class RequireApprovedTests(unittest.TestCase):
    def test_calcofi_requires_approved_manifest(self) -> None:
        entry = require_approved("calcofi_cufes")
        self.assertIn("NOAA ERDDAP", entry["license"])
        self.assertIn("license_text", entry)
        self.assertIn("CalCOFI", attribution_for("calcofi_cufes"))
        self.assertEqual(
            attribution_for("calcofi_cufes"),
            "NOAA SWFSC / CalCOFI, erdCalCOFIcufes; "
            "https://oceanview.pfeg.noaa.gov/erddap/tabledap/erdCalCOFIcufes.html",
        )

    def test_glorys_blocked(self) -> None:
        with self.assertRaises(SourceNotApprovedError):
            require_approved("glorys")

    def test_pending_glider_blocked(self) -> None:
        with self.assertRaises(SourceNotApprovedError):
            require_approved("ioos_glider_dac")

    def test_enabled_without_approved_fails(self) -> None:
        manifest = {
            "sources": {
                "bad_source": {
                    "module": "fishai.ingestion.biology.calcofi_cufes",
                    "license": "TEST",
                    "license_url": "https://example.com",
                    "attribution": "Test",
                    "status": "pending",
                    "enabled": True,
                }
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SOURCES.yaml"
            path.write_text(yaml.dump(manifest), encoding="utf-8")
            with self.assertRaises(SourceNotApprovedError):
                require_approved("bad_source", path=path)


if __name__ == "__main__":
    unittest.main()
