"""NDBC and glider fetcher tests (mock HTTP)."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from fishai.ingestion.sensors.sources.gliders import build_glider_profile_url, list_active
from fishai.ingestion.sensors.sources.ndbc import build_ndbc_url, fetch_ndbc, list_stations


class NdbcTests(unittest.TestCase):
    def test_build_ndbc_url_encodes_time(self) -> None:
        t0 = datetime(2026, 9, 27, 0, 0, tzinfo=timezone.utc)
        t1 = datetime(2026, 9, 28, 0, 0, tzinfo=timezone.utc)
        url = build_ndbc_url(t0, t1, (32.0, 35.0, -121.0, -117.0))
        self.assertIn("%3C%3D", url)
        self.assertIn("%3E%3D", url)

    def test_fetch_drops_no_wtmp_stations(self) -> None:
        csv = (
            "station,time,latitude,longitude,WD,WSPD,GST,WVHT,DPD,APD,MWD,BAR,ATMP,WTMP,DEWP\n"
            "units,,,,,,,,,,,,,,\n"
            "46025,2026-09-28T00:00:00Z,33.0,-120.0,,,,,,,,,,18.0,\n"
            "SHORE,2026-09-28T00:00:00Z,33.5,-119.0,,,,,,,,,,,\n"
        )
        client = MagicMock()
        resp = MagicMock(status_code=200, text=csv)
        client.get.return_value = resp
        t0 = datetime(2026, 9, 27, tzinfo=timezone.utc)
        t1 = datetime(2026, 9, 28, tzinfo=timezone.utc)
        df = fetch_ndbc(t0, t1, (32.0, 35.0, -121.0, -117.0), client=client)
        self.assertEqual(sorted(df["station"].astype(str).unique()), ["46025"])

    def test_list_stations_filters_wtmp(self) -> None:
        csv = (
            "station,WTMP\n"
            "units,\n"
            "46025,17.5\n"
            "NOSST,\n"
        )
        client = MagicMock()
        client.get.return_value = MagicMock(status_code=200, text=csv)
        stations = list_stations((32.0, 35.0, -121.0, -117.0), client=client)
        self.assertEqual(stations, ["46025"])


class GliderTests(unittest.TestCase):
    def test_list_active_parses_csv(self) -> None:
        csv = (
            "datasetID,minTime,maxTime\n"
            "units,,\n"
            "sp041-20250920T1940,2026-09-20T19:40:00Z,2026-09-28T00:00:00Z\n"
        )
        client = MagicMock()
        client.get.return_value = MagicMock(status_code=200, text=csv)
        since = datetime(2026, 9, 20, tzinfo=timezone.utc)
        ids = list_active((32.0, 35.0, -121.0, -117.0), since, client=client)
        self.assertEqual(ids, ["sp041-20250920T1940"])

    def test_profile_url_percent_encoding(self) -> None:
        t0 = datetime(2026, 9, 27, tzinfo=timezone.utc)
        t1 = datetime(2026, 9, 28, tzinfo=timezone.utc)
        url = build_glider_profile_url("sp041-20250920T1940", t0, t1)
        self.assertIn("%3C%3D", url)


if __name__ == "__main__":
    unittest.main()
