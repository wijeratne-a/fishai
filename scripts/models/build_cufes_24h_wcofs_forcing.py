#!/usr/bin/env python3
"""Materialize WCOFS 24 h forcing sidecars for rolling-origin cutoffs (public data only)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from fishai.models.cufes_24h_wcofs_forcing import (  # noqa: E402
    CUFES_TEST_END,
    build_holdout_forcing_table,
    pooled_forcing_label,
    resolve_24h_forcing,
)


def _parse_cutoffs(raw: list[str]) -> list[dt.date]:
    return [dt.date.fromisoformat(x) for x in raw]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--events-parquet",
        type=Path,
        default=REPO / "data/processed/calcofi_cufes/cufes_events.parquet",
    )
    parser.add_argument(
        "--counts-parquet",
        type=Path,
        default=REPO / "data/processed/calcofi_cufes/cufes_counts.parquet",
    )
    parser.add_argument(
        "--covariates-parquet",
        type=Path,
        default=REPO / "data/processed/calcofi_cufes/cufes_training_covariates.parquet",
    )
    parser.add_argument("--species", choices=("sardine", "anchovy"), required=True)
    parser.add_argument(
        "--cutoffs-json",
        type=Path,
        default=REPO / "prereg/cufes_forecast_temporal_holdout_scores.json",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPO / "artifacts/cufes_24h_wcofs_prediction/forcing",
    )
    args = parser.parse_args()

    if not args.events_parquet.is_file():
        print(f"BLOCKED: missing events table {args.events_parquet}", file=sys.stderr)
        return 2

    cutoffs_payload = json.loads(args.cutoffs_json.read_text(encoding="utf-8"))
    cutoffs = _parse_cutoffs(list(cutoffs_payload.get("cutoffs") or []))
    if not cutoffs:
        print("BLOCKED: no cutoffs in cutoffs-json", file=sys.stderr)
        return 2

    events = pd.read_parquet(args.events_parquet)
    counts = pd.read_parquet(args.counts_parquet)
    cov = pd.read_parquet(args.covariates_parquet)
    taxon_col = "taxon" if "taxon" in counts.columns else "species"
    sp_counts = counts[counts[taxon_col].str.lower() == args.species]
    merged = events.merge(sp_counts, on="event_id", how="inner", suffixes=("", "_y"))
    merged = merged.merge(cov, on="event_id", how="inner", suffixes=("", "_cov"))

    if "event_mid_time" in merged.columns:
        merged["event_day"] = pd.to_datetime(merged["event_mid_time"], utc=True).dt.date
    elif "time_idx" in merged.columns:
        origin = dt.date(1990, 1, 1)
        merged["event_day"] = merged["time_idx"].apply(lambda ti: origin + dt.timedelta(days=int(ti) - 1))

    out_species = args.out_dir / args.species
    out_species.mkdir(parents=True, exist_ok=True)
    summary: dict[str, object] = {"species": args.species, "cutoffs": {}}

    for cutoff in cutoffs:
        hold = merged[merged["event_day"] == cutoff + dt.timedelta(days=1)].copy()
        if hold.empty:
            summary["cutoffs"][cutoff.isoformat()] = {"n_holdout": 0}
            continue
        hold["event_id"] = hold["event_id"].astype(str)
        table = build_holdout_forcing_table(hold, cutoff)
        out_path = out_species / f"{cutoff.isoformat()}.parquet"
        table.to_parquet(out_path, index=False)
        res = resolve_24h_forcing(cutoff, cutoff + dt.timedelta(days=1))
        summary["cutoffs"][cutoff.isoformat()] = {
            "n_holdout": int(len(table)),
            "resolution_counts": dict(table.attrs.get("resolution_counts", {})),
            "sample_resolution": asdict(res),
        }

    summary["pooled_forcing_label"] = pooled_forcing_label(cutoffs)
    summary["cufes_test_end"] = CUFES_TEST_END.isoformat()
    manifest_path = out_species / "forcing_build_summary.json"
    manifest_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
