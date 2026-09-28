#!/usr/bin/env python3
"""Recompute Step 3 CUFES event counts from bot1 parquets (no modeling filters)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
EVENTS = REPO / "data/processed/calcofi_cufes/cufes_events.parquet"
COUNTS = REPO / "data/processed/calcofi_cufes/cufes_counts.parquet"
TEST_START = "2018-01-01"
TEST_END = "2022-04-27"


def main() -> None:
    events = pd.read_parquet(EVENTS)
    counts = pd.read_parquet(COUNTS)
    events["time"] = pd.to_datetime(events["time"])
    test_end = pd.Timestamp(TEST_END) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    if events["time"].dt.tz is not None:
        test_end = test_end.tz_localize(events["time"].dt.tz)
    ev_test = events[
        (events["time"] >= pd.Timestamp(TEST_START, tz=events["time"].dt.tz))
        & (events["time"] <= test_end)
    ]
    print("full_events", len(events))
    print("test_window_events", len(ev_test))
    for taxon in ("sardine", "anchovy"):
        c = counts[(counts["taxon"] == taxon) & (counts["event_id"].isin(ev_test["event_id"]))]
        print(taxon, "positive", int((c["count"] > 0).sum()))
    spring = ev_test[ev_test["time"].dt.month.between(2, 5)]
    years = sorted(spring["time"].dt.year.unique())
    print("spring_seasons_with_events", len(years), years)


if __name__ == "__main__":
    main()
