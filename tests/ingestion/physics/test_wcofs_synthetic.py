"""WCOFS fetch/subset tests with in-memory NetCDF (no network)."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fishai.ingestion.physics.sources.wcofs import cycle_available, fetch_cycle
from wcofs_fixtures import write_mini_wcofs_bytes


def _list_keys_for_day(day: dt.date, lead: str = "n024") -> list[str]:
    ymd = day.strftime("%Y%m%d")
    return [f"wcofs/netcdf/{day:%Y/%m/%d}/wcofs.t03z.{ymd}.fields.{lead}.nc"]


def _list_keys_for_day(day: dt.date, lead: str = "n024") -> list[str]:
    ymd = day.strftime("%Y%m%d")
    return [f"wcofs/netcdf/{day:%Y/%m/%d}/wcofs.t03z.{ymd}.fields.{lead}.nc"]


def test_cycle_available_uses_injected_head() -> None:
    day = dt.date(2026, 9, 1)

    def list_keys(_prefix: str) -> list[str]:
        return _list_keys_for_day(day)

    assert cycle_available(day, head_fn=lambda _u: True, list_keys=list_keys)
    assert not cycle_available(day, head_fn=lambda _u: False, list_keys=list_keys)


def test_fetch_cycle_subset_and_features() -> None:
    payload = write_mini_wcofs_bytes()
    bbox = (32.0, 35.0, -121.0, -117.0)

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        return payload

    day = dt.date(2026, 9, 28)

    def list_keys(_prefix: str) -> list[str]:
        return _list_keys_for_day(day, "n024") + _list_keys_for_day(day, "n003")

    ds = fetch_cycle(
        day,
        ["n003"],
        bbox,
        get_fn=fake_get,
        head_fn=lambda _u: True,
        list_keys=list_keys,
    )
    assert "bottom_temp" in ds
    assert "mld_m" in ds
    assert ds.attrs["source"] == "wcofs"
