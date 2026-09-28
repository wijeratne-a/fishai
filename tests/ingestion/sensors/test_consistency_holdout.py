"""Consistency and holdout metric tests on synthetic fields."""

from __future__ import annotations

import unittest

import numpy as np
import pandas as pd
import xarray as xr

from fishai.ingestion.sensors.internal.consistency import score_cycle
from fishai.ingestion.sensors.internal.holdout import mixed_layer_depth, score_holdout, thermocline_depth


class ConsistencyTests(unittest.TestCase):
    def test_vector_corr_perfect_match(self) -> None:
        lats = np.linspace(32, 34, 5)
        lons = np.linspace(-120, -118, 5)
        model = xr.Dataset(
            {
                "temp": (("eta_rho", "xi_rho"), np.full((5, 5), 18.0)),
                "u_east": (("eta_rho", "xi_rho"), np.full((5, 5), 0.2)),
                "v_north": (("eta_rho", "xi_rho"), np.full((5, 5), 0.1)),
            },
            coords={"lat_rho": (("eta_rho", "xi_rho"), np.broadcast_to(lats[:, None], (5, 5))),
                    "lon_rho": (("eta_rho", "xi_rho"), np.broadcast_to(lons[None, :], (5, 5)))},
        )
        hfr = xr.Dataset(
            {
                "water_u": (("time", "latitude", "longitude"), np.full((1, 5, 5), 0.2)),
                "water_v": (("time", "latitude", "longitude"), np.full((1, 5, 5), 0.1)),
            },
            coords={"time": [np.datetime64("2026-09-28T09:00:00")], "latitude": lats, "longitude": lons},
        )
        ndbc = pd.DataFrame(
            {"latitude": [33.0], "longitude": [-119.0], "WTMP": [18.0]}
        )
        cfg = {
            "consistency": {
                "current_vector_corr": {"pass": 0.9, "degraded": 0.5},
                "current_rmse_ms": {"pass": 0.05, "degraded": 0.2},
                "sst_bias_c": {"pass": 0.1, "degraded": 0.5},
                "sst_rmse_c": {"pass": 0.1, "degraded": 0.5},
            }
        }
        scores = score_cycle(model, {"hfr": hfr, "ndbc": ndbc}, cfg=cfg)
        corr_row = scores[(scores["metric"] == "vector_corr") & (scores["grid_mode"] == "native")].iloc[0]
        self.assertGreaterEqual(corr_row["value"], 0.99)
        self.assertEqual(corr_row["status"], "PASS")


class HoldoutTests(unittest.TestCase):
    def test_mld_and_thermocline(self) -> None:
        depth = np.array([0, 10, 20, 30, 50.0])
        temp = np.array([20.0, 19.9, 18.0, 15.0, 12.0])
        mld = mixed_layer_depth(depth, temp, ref_depth_m=10.0, delta_c=0.2)
        self.assertEqual(mld, 20.0)
        tc = thermocline_depth(depth, temp)
        self.assertGreater(tc, 10.0)

    def test_holdout_independent_false_by_default(self) -> None:
        profiles = pd.DataFrame(
            {
                "profile_id": [1, 1, 1],
                "depth": [5, 25, 40],
                "temperature": [20.0, 17.0, 14.0],
                "time": pd.to_datetime(["2026-09-28T00:00:00Z"] * 3, utc=True),
            }
        )
        model = xr.Dataset({"temp": (("s_rho",), np.array([16.0, 15.0]))}, coords={"s_rho": [0, 1]})
        cfg = {"holdout": {"independent_confirmed": False, "mld_delta_c": 0.2, "depth_bands_m": [[20, 50]]}}
        out = score_holdout(model, profiles, cfg=cfg)
        self.assertEqual(out.iloc[0]["check_type"], "holdout")
        self.assertFalse(out.iloc[0]["independent"])


if __name__ == "__main__":
    unittest.main()
