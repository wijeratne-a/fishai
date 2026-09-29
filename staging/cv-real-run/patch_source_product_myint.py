#!/usr/bin/env python3
"""Staging-only: align source_product with glorys_product_for_date on local training parquet.

PR #28 evidence table (2026-09-29 build) had 145 post-2021-06-30 rows still stamped ``my``.
Do not commit patched parquet; run before dry-run CV when using that table.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

MY = "cmems_mod_glo_phy_my_0.083deg_P1D-m"
MYINT = "cmems_mod_glo_phy_myint_0.083deg_P1D-m"
BOUNDARY = pd.Timestamp("2021-06-30", tz="UTC")


def expected_product(ts: pd.Timestamp) -> str:
    return MY if ts.date() <= BOUNDARY.date() else MYINT


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    cov_path = root / "data/processed/calcofi_cufes/cufes_training_covariates.parquet"
    ev_path = root / "data/processed/calcofi_cufes/cufes_events.parquet"
    cov = pd.read_parquet(cov_path)
    ev = pd.read_parquet(ev_path)
    ev["time"] = pd.to_datetime(ev["time"], utc=True)
    times = ev.set_index("event_id")["time"]
    exp = cov["event_id"].map(lambda e: expected_product(times[e]))
    mask = cov["source_product"] != exp
    n = int(mask.sum())
    if n:
        cov.loc[mask, "source_product"] = exp[mask]
        cov.to_parquet(cov_path, index=False)
    print(f"patched {n} source_product row(s) in {cov_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
