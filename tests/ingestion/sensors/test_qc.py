"""QC flag tests."""

from __future__ import annotations

import unittest

import numpy as np
import pandas as pd
import xarray as xr

from fishai.ingestion.sensors.internal.qc import QC_RADAR_HDOP, QC_RADAR_SITES, QC_RANGE, qc_hfradar, qc_ndbc


class QcTests(unittest.TestCase):
    def test_radar_masks_hdop_and_sites(self) -> None:
        ds = xr.Dataset(
            {
                "water_u": (("time", "latitude", "longitude"), np.array([[[0.1]]])),
                "water_v": (("time", "latitude", "longitude"), np.array([[[0.1]]])),
                "hdop": (("time", "latitude", "longitude"), np.array([[[2.0]]])),
                "number_of_sites": (("time", "latitude", "longitude"), np.array([[[1]]])),
            },
            coords={"time": [np.datetime64("2026-09-28T09:00:00")], "latitude": [33.0], "longitude": [-120.0]},
        )
        out = qc_hfradar(ds, {"radar_hdop_max": 1.25, "radar_min_sites": 2, "range": {}})
        flags = int(out["qc_flags"].values[0, 0, 0])
        self.assertTrue(flags & QC_RADAR_HDOP)
        self.assertTrue(flags & QC_RADAR_SITES)
        self.assertTrue(np.isnan(out["water_u"].values[0, 0, 0]))

    def test_ndbc_range_flag(self) -> None:
        df = pd.DataFrame(
            {
                "station": ["a"],
                "time": pd.to_datetime(["2026-09-28T00:00:00Z"], utc=True),
                "WTMP": [50.0],
            }
        )
        out = qc_ndbc(
            df,
            {
                "range": {"wtmp_c": [-2.0, 35.0]},
                "spike_window": 3,
                "spike_threshold_sigma": 4,
                "flat_line_min_points": 6,
                "flat_line_epsilon": 1e-4,
                "staleness_hours": {"ndbc": 1000},
            },
        )
        self.assertTrue(int(out["qc_flags"].iloc[0]) & QC_RANGE)


if __name__ == "__main__":
    unittest.main()
