#!/usr/bin/env python3
"""Recompute Step 3 CUFES event counts from PR #4 QC parquets (no modeling filters)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
EVENTS = REPO / "data/processed/calcofi_cufes/cufes_events.parquet"
COUNTS = REPO / "data/processed/calcofi_cufes/cufes_counts.parquet"
EXPECTED_EVENTS = 14_592
TEST_START = "2018-01-01"
TEST_END = "2022-04-27"


def git_head() -> str:
    out = subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"],
        text=True,
    )
    return out.strip()


def main() -> None:
    if not EVENTS.is_file():
        print(f"missing QC event table: {EVENTS}", file=sys.stderr)
        sys.exit(1)

    commit = git_head()
    events = pd.read_parquet(EVENTS)
    n_events = len(events)
    print("events_path", EVENTS.relative_to(REPO))
    print("git_commit", commit)
    print("full_events", n_events)
    if n_events != EXPECTED_EVENTS:
        print(
            f"ERROR: expected {EXPECTED_EVENTS} QC events (PR #4), got {n_events}",
            file=sys.stderr,
        )
        sys.exit(1)

    counts = pd.read_parquet(COUNTS)
    events["time"] = pd.to_datetime(events["time"])
    tz = events["time"].dt.tz
    test_end = pd.Timestamp(TEST_END) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    if tz is not None:
        test_end = test_end.tz_localize(tz)
    ev_test = events[
        (events["time"] >= pd.Timestamp(TEST_START, tz=tz))
        & (events["time"] <= test_end)
    ]
    print("test_window_events", len(ev_test))
    for taxon in ("sardine", "anchovy"):
        c = counts[(counts["taxon"] == taxon) & (counts["event_id"].isin(ev_test["event_id"]))]
        print(taxon, "positive", int((c["count"] > 0).sum()))
    spring = ev_test[ev_test["time"].dt.month.between(2, 5)]
    years = sorted(spring["time"].dt.year.unique())
    print("spring_seasons_with_events", len(years), years)


if __name__ == "__main__":
    main()
