"""HTTP pacing and sync governance tests."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch

from fishai.ingestion.sources import SourceNotApprovedError
from fishai.ingestion.sensors.internal.http import HttpClient, reset_http_client
from fishai.ingestion.sensors.internal.sync import parse_since


class HttpClientTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_http_client()

    def test_min_interval_between_requests(self) -> None:
        client = HttpClient(min_interval_s=0.2, max_retries=1)
        resp = MagicMock(status_code=200, text="ok")
        with patch("fishai.ingestion.sensors.internal.http.requests.get", return_value=resp) as mock_get:
            t0 = time.monotonic()
            client.get("https://example.com/a")
            client.get("https://example.com/b")
            elapsed = time.monotonic() - t0
        self.assertGreaterEqual(elapsed, 0.2)
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(len(client.request_log), 2)


class SyncGovernanceTests(unittest.TestCase):
    def test_parse_since_hours(self) -> None:
        from datetime import datetime, timezone

        now = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
        dt = parse_since("24h", now=now)
        self.assertEqual(dt.day, 27)

    def test_glider_sync_blocked(self) -> None:
        with patch("fishai.ingestion.sensors.internal.sync.fetch_hfr") as mock_hfr:
            import xarray as xr

            mock_hfr.return_value = xr.Dataset()
            with patch("fishai.ingestion.sensors.internal.sync.qc_hfradar", side_effect=lambda ds, qc: ds):
                with patch("fishai.ingestion.sensors.internal.sync.append_hfr_zarr", return_value="z"):
                    with patch("fishai.ingestion.sensors.internal.sync.list_stations", return_value=[]):
                        with patch(
                            "fishai.ingestion.sensors.internal.sync.fetch_ndbc",
                            return_value=__import__("pandas").DataFrame(),
                        ):
                            with patch("fishai.ingestion.sensors.internal.sync.qc_ndbc", side_effect=lambda df, qc: df):
                                with patch("fishai.ingestion.sensors.internal.sync.write_ndbc_parquet", return_value=None):
                                    from fishai.ingestion.sensors.internal.sync import run_sync

                                    report = run_sync("24h")
        self.assertIn("skipped", report["sources"]["ioos_glider_dac"])


if __name__ == "__main__":
    unittest.main()
