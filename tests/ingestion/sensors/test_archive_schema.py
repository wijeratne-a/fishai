"""Sensor archive outputs: plain lat/lon, no geometry; under data/processed/."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from fishai.ingestion.sensors.internal.archive import (
    _prepare_tabular_archive,
    write_glider_parquet,
    write_ndbc_parquet,
)
class ArchiveSchemaTests(unittest.TestCase):
    def test_prepare_tabular_renames_positions(self) -> None:
        df = pd.DataFrame(
            {
                "station": ["46025"],
                "latitude": [33.0],
                "longitude": [-120.0],
                "WTMP": [18.0],
            }
        )
        out = _prepare_tabular_archive(df)
        self.assertIn("lat", out.columns)
        self.assertIn("lon", out.columns)
        self.assertNotIn("latitude", out.columns)
        self.assertNotIn("longitude", out.columns)
        self.assertNotIn("geometry", out.columns)

    def test_ndbc_parquet_written_under_processed(self) -> None:
        df = pd.DataFrame(
            {
                "station": ["46025"],
                "time": pd.to_datetime(["2026-09-28T00:00:00Z"], utc=True),
                "latitude": [33.0],
                "longitude": [-120.0],
                "WTMP": [18.0],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            processed = Path(tmp) / "data" / "processed" / "sensors" / "ndbc"
            # Patch REPO_ROOT for this write by using real layout under tmp
            import fishai.ingestion.sensors.internal.archive as arch
            import fishai.ingestion.sensors.internal.config as cfg_mod

            old_root = cfg_mod.REPO_ROOT
            cfg_mod.REPO_ROOT = Path(tmp)
            arch.REPO_ROOT = Path(tmp)
            try:
                cfg = {
                    "paths": {"ndbc_parquet_root": "data/processed/sensors/ndbc"},
                }
                path = write_ndbc_parquet(df, datetime(2026, 9, 28, tzinfo=timezone.utc), cfg)
                self.assertIsNotNone(path)
                schema = pq.read_schema(path)
                names = set(schema.names)
                self.assertIn("lat", names)
                self.assertIn("lon", names)
                self.assertNotIn("latitude", names)
                self.assertNotIn("geometry", names)
            finally:
                cfg_mod.REPO_ROOT = old_root
                arch.REPO_ROOT = old_root

    def test_glider_parquet_plain_lat_lon(self) -> None:
        df = pd.DataFrame(
            {
                "profile_id": [1],
                "time": pd.to_datetime(["2026-09-28T00:00:00Z"], utc=True),
                "latitude": [33.0],
                "longitude": [-120.0],
                "depth": [10.0],
                "temperature": [18.0],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            import fishai.ingestion.sensors.internal.archive as arch
            import fishai.ingestion.sensors.internal.config as cfg_mod

            old_root = cfg_mod.REPO_ROOT
            cfg_mod.REPO_ROOT = Path(tmp)
            arch.REPO_ROOT = Path(tmp)
            try:
                cfg = {"paths": {"gliders_parquet_root": "data/processed/sensors/gliders"}}
                path = write_glider_parquet(
                    df, "test-glider", datetime(2026, 9, 28, tzinfo=timezone.utc), cfg
                )
                names = set(pq.read_schema(path).names)
                self.assertIn("lat", names)
                self.assertIn("lon", names)
                self.assertNotIn("latitude", names)
            finally:
                cfg_mod.REPO_ROOT = old_root
                arch.REPO_ROOT = old_root


if __name__ == "__main__":
    unittest.main()
