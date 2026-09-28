"""WCOFS cycle loading for sensor consistency/holdout."""

from __future__ import annotations

import datetime as dt
import unittest
from unittest import mock

import xarray as xr

from fishai.ingestion.sensors.internal.model_loader import load_wcofs_cycle
from fishai.physics.store import CycleNotAvailable, WcofsDayFailed


class ModelLoaderTests(unittest.TestCase):
    def test_missing_cycle_returns_none(self) -> None:
        with mock.patch(
            "fishai.ingestion.sensors.internal.model_loader.open_wcofs_cycle",
            side_effect=CycleNotAvailable("missing"),
        ):
            out = load_wcofs_cycle("20260101")
        self.assertIsNone(out)

    def test_tombstone_failure_propagates(self) -> None:
        with mock.patch(
            "fishai.ingestion.sensors.internal.model_loader.open_wcofs_cycle",
            side_effect=WcofsDayFailed(
                "failed",
                reason="wcofs_nowcast_missing",
                target_date=dt.date(2026, 9, 28),
            ),
        ):
            with self.assertRaises(WcofsDayFailed):
                load_wcofs_cycle("20260928")

    def test_open_delegates_to_physics_store(self) -> None:
        ds = xr.Dataset({"temp": ((), 1.0)})
        with mock.patch(
            "fishai.ingestion.sensors.internal.model_loader.open_wcofs_cycle",
            return_value=ds,
        ) as open_mock:
            out = load_wcofs_cycle("20260928")
        self.assertIs(out, ds)
        open_mock.assert_called_once()
        self.assertEqual(open_mock.call_args[0][0].isoformat(), "2026-09-28")


if __name__ == "__main__":
    unittest.main()
