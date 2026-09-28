"""HF radar URL construction and sync window tests."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import numpy as np
import xarray as xr

from fishai.ingestion.sensors.internal.http import HttpClient, reset_http_client
from fishai.ingestion.sensors.sources.hfradar import (
    build_hfr_griddap_url,
    closed_hour_window,
    fetch_hfr,
)


class HfradarUrlTests(unittest.TestCase):
    def test_relative_last_not_parenthesized(self) -> None:
        url = build_hfr_griddap_url(
            (32.0, 35.0, -121.0, -117.0),
            use_relative_last=True,
            relative_start="last-5",
        )
        self.assertIn("[last-5:1:last]", url)
        self.assertNotIn("[(last-5", url)

    def test_closed_hour_window_skips_partial(self) -> None:
        now = datetime(2026, 9, 28, 10, 45, tzinfo=timezone.utc)
        t0, t1 = closed_hour_window(now=now, hours=24)
        self.assertEqual(t1, datetime(2026, 9, 28, 9, 0, tzinfo=timezone.utc))
        self.assertEqual(t0, datetime(2026, 9, 27, 10, 0, tzinfo=timezone.utc))


class HfradarFetchTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_http_client()

    def test_fetch_hfr_parses_netcdf(self) -> None:
        times = np.array(["2026-09-28T08:00:00", "2026-09-28T09:00:00"], dtype="datetime64[ns]")
        lats = np.linspace(32, 35, 3)
        lons = np.linspace(-121, -117, 4)
        ds = xr.Dataset(
            {
                "water_u": (("time", "latitude", "longitude"), np.ones((2, 3, 4))),
                "water_v": (("time", "latitude", "longitude"), np.zeros((2, 3, 4))),
                "DOPx": (("time", "latitude", "longitude"), np.ones((2, 3, 4))),
                "DOPy": (("time", "latitude", "longitude"), np.ones((2, 3, 4))),
                "hdop": (("time", "latitude", "longitude"), np.ones((2, 3, 4)) * 0.5),
                "number_of_sites": (("time", "latitude", "longitude"), np.ones((2, 3, 4)) * 3),
                "number_of_radials": (("time", "latitude", "longitude"), np.ones((2, 3, 4)) * 5),
            },
            coords={"time": times, "latitude": lats, "longitude": lons},
        )
        client = HttpClient(min_interval_s=0)
        resp = MagicMock(status_code=200, text="", content=b"nc")
        client.get = MagicMock(return_value=resp)  # type: ignore[method-assign]
        t0 = datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc)
        t1 = datetime(2026, 9, 28, 9, 0, tzinfo=timezone.utc)
        with patch("xarray.open_dataset", return_value=ds):
            out = fetch_hfr(t0, t1, (32.0, 35.0, -121.0, -117.0), client=client)
        self.assertEqual(out.sizes["time"], 2)


if __name__ == "__main__":
    unittest.main()
