"""WCOFS fetch/subset tests with in-memory NetCDF (no network)."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fishai.ingestion.physics.sources.wcofs import cycle_available, fetch_cycle
from wcofs_fixtures import write_mini_wcofs_bytes


def test_cycle_available_uses_injected_head() -> None:
    assert cycle_available(dt.date(2026, 9, 1), head_fn=lambda _u: True)
    assert not cycle_available(dt.date(2026, 9, 1), head_fn=lambda _u: False)


def test_fetch_cycle_subset_and_features() -> None:
    payload = write_mini_wcofs_bytes()
    bbox = (32.0, 35.0, -121.0, -117.0)

    def fake_get(url: str, **kwargs: Any) -> bytes:  # noqa: ARG001
        return payload

    ds = fetch_cycle(
        dt.date(2026, 9, 28),
        ["n003"],
        bbox,
        get_fn=fake_get,
        head_fn=lambda _u: True,
    )
    assert "bottom_temp" in ds
    assert "mld_m" in ds
    assert ds.attrs["source"] == "wcofs"
