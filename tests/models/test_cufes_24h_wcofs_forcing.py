"""WCOFS-first 24 h forcing resolution (public archive boundaries)."""

from __future__ import annotations

import datetime as dt

from fishai.models.cufes_24h_wcofs_forcing import (
    pooled_forcing_label,
    resolve_24h_forcing,
)


def test_historical_cutoff_uses_proxy_fallback() -> None:
    cutoff = dt.date(2018, 9, 20)
    event = cutoff + dt.timedelta(days=1)
    res = resolve_24h_forcing(cutoff, event)
    assert res.source == "proxy_fallback"
    assert "2024" in res.reason or "archive" in res.reason


def test_pooled_label_proxy_for_egg_record_cutoffs() -> None:
    cutoffs = [
        dt.date(1998, 2, 26),
        dt.date(2022, 4, 12),
    ]
    assert pooled_forcing_label(cutoffs) == "proxy_fallback"


def test_non_24h_horizon_rejects_wcofs() -> None:
    cutoff = dt.date(2025, 6, 1)
    event = cutoff + dt.timedelta(days=2)
    res = resolve_24h_forcing(cutoff, event)
    assert res.source == "proxy_fallback"
    assert "24h" in res.reason
