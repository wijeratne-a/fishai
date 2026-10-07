#!/usr/bin/env python3
"""Export R model-ready tables for Pacific mackerel encounter (binomial) fit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from fishai.ingestion.adult.constants import (  # noqa: E402
    MACKEREL_EVENTS_PATH,
    MACKEREL_MODEL_READY_DIR,
    MACKEREL_SCIENTIFIC_NAME,
    MACKEREL_TRAINING_TABLE_PATH,
)
from fishai.ingestion.physics.cufes_training_covariates import TRAINING_OUTPUT_COLUMNS  # noqa: E402

TAXON = "pacific_mackerel"
NEARSHORE_REFERENCE_EFFORT_MIN = 2.0
NEARSHORE_SOURCE = "swfsc_cps_nearshore_set_catch"


def _events_for_r(events: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "event_id": events["event_id"].astype(str),
            "time": pd.to_datetime(events["start_time"], utc=True),
            "lat": events["start_latitude"].astype(float),
            "lon": events["start_longitude"].astype(float),
            "stop_time": pd.to_datetime(events["stop_time"], utc=True),
            "stop_lat": events["stop_latitude"].astype(float),
            "stop_lon": events["stop_longitude"].astype(float),
            "effort_duration_min": events["effort_duration_min"].astype(float),
            "duration_min": events["effort_duration_min"].astype(float),
            "volume_m3": events["effort_duration_min"].astype(float),
            "pump_readings_used": 1,
            "short_event": False,
        }
    )


def export_model_tables(
    *,
    events_path: Path = MACKEREL_EVENTS_PATH,
    training_path: Path = MACKEREL_TRAINING_TABLE_PATH,
    out_dir: Path = MACKEREL_MODEL_READY_DIR,
) -> dict[str, object]:
    events_raw = pd.read_parquet(events_path)
    table = pd.read_parquet(training_path)
    obs = table[table["species"] == MACKEREL_SCIENTIFIC_NAME].copy()
    if obs.empty:
        raise SystemExit(f"no training rows for species={MACKEREL_SCIENTIFIC_NAME!r}")
    obs = obs[~obs["biology_excluded"].fillna(False).astype(bool)].copy()
    obs = obs[~obs["excluded"].fillna(False).astype(bool)].copy()
    near = obs["observation_source"] == NEARSHORE_SOURCE
    obs.loc[near, "effort_duration_min"] = obs.loc[near, "effort_duration_min"].fillna(
        NEARSHORE_REFERENCE_EFFORT_MIN
    )
    obs = obs[obs["effort_duration_min"].notna() & (obs["effort_duration_min"] > 0)].copy()
    if obs.empty:
        raise SystemExit("no eligible rows after biology/effort QC")

    counts = pd.DataFrame(
        {
            "event_id": obs["event_id"].astype(str),
            "taxon": TAXON,
            "count": obs["encounter"].astype(int),
        }
    )
    events = _events_for_r(events_raw)
    if "observation_source" in events_raw.columns:
        near_ids = set(
            events_raw.loc[
                events_raw["observation_source"] == NEARSHORE_SOURCE, "event_id"
            ].astype(str)
        )
    else:
        near_ids = set()
    if near_ids:
        near_mask = events["event_id"].isin(near_ids)
        events.loc[near_mask, "effort_duration_min"] = events.loc[
            near_mask, "effort_duration_min"
        ].fillna(NEARSHORE_REFERENCE_EFFORT_MIN)
        events.loc[near_mask, "duration_min"] = events.loc[near_mask, "effort_duration_min"]
        events.loc[near_mask, "volume_m3"] = events.loc[near_mask, "effort_duration_min"]

    cov_cols = list(TRAINING_OUTPUT_COLUMNS)
    cov = obs.drop_duplicates(subset=["event_id"], keep="first")[cov_cols].copy()

    out_dir.mkdir(parents=True, exist_ok=True)
    events_path_out = out_dir / "adult_mackerel_events.parquet"
    counts_path_out = out_dir / "adult_mackerel_counts.parquet"
    cov_path_out = out_dir / "adult_mackerel_covariates.parquet"
    events.to_parquet(events_path_out, index=False)
    counts.to_parquet(counts_path_out, index=False)
    cov.to_parquet(cov_path_out, index=False)

    summary = {
        "species": MACKEREL_SCIENTIFIC_NAME,
        "taxon": TAXON,
        "n_fit_rows": int(len(counts)),
        "n_presences": int((counts["count"] > 0).sum()),
        "n_absences": int((counts["count"] == 0).sum()),
        "events_path": str(events_path_out),
        "counts_path": str(counts_path_out),
        "covariates_path": str(cov_path_out),
    }
    summary_path = out_dir / "adult_mackerel_export_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=MACKEREL_EVENTS_PATH)
    parser.add_argument("--training", type=Path, default=MACKEREL_TRAINING_TABLE_PATH)
    parser.add_argument("--out-dir", type=Path, default=MACKEREL_MODEL_READY_DIR)
    args = parser.parse_args()
    summary = export_model_tables(
        events_path=args.events,
        training_path=args.training,
        out_dir=args.out_dir,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
