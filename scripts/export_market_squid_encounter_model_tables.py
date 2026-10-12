#!/usr/bin/env python3
"""Export R model-ready tables for market squid encounter (all sizes; not adult)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from fishai.ingestion.adult.constants import DEFAULT_DROPS_PATH, DEFAULT_PROCESSED_DIR  # noqa: E402
from fishai.ingestion.adult.squid_encounter import (  # noqa: E402
    ENCOUNTER_LABEL,
    MARKET_SQUID_CANONICAL,
)
from fishai.ingestion.physics.cufes_training_covariates import TRAINING_OUTPUT_COLUMNS  # noqa: E402

SQUID_EVENTS = DEFAULT_PROCESSED_DIR / "market_squid_encounter_events.parquet"
SQUID_TABLE = DEFAULT_PROCESSED_DIR / "market_squid_encounter_training_table.parquet"
SQUID_DROPS = DEFAULT_PROCESSED_DIR / "market_squid_encounter_covariate_drops.parquet"
SQUID_DROP_SUMMARY = DEFAULT_PROCESSED_DIR / "market_squid_encounter_covariate_drop_summary.json"
MODEL_DIR = DEFAULT_PROCESSED_DIR / "model_ready"
TAXON = "market_squid_encounter"
NEARSHORE_REFERENCE_EFFORT_MIN = 2.0
NEARSHORE_SOURCE = "swfsc_cps_nearshore_set_catch"


def _events_for_r(events: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(
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
    return out


def export_model_tables(
    *,
    events_path: Path = SQUID_EVENTS,
    training_path: Path = SQUID_TABLE,
    out_dir: Path = MODEL_DIR,
) -> dict[str, object]:
    events_raw = pd.read_parquet(events_path)
    table = pd.read_parquet(training_path)
    obs = table[table["species"] == MARKET_SQUID_CANONICAL].copy()
    if obs.empty:
        raise SystemExit(f"no training rows for species={MARKET_SQUID_CANONICAL!r}")

    obs = obs[~obs["biology_excluded"].fillna(False).astype(bool)].copy()
    obs = obs[~obs["excluded"].fillna(False).astype(bool)].copy()
    near = obs["observation_source"] == NEARSHORE_SOURCE
    obs.loc[near, "effort_duration_min"] = obs.loc[near, "effort_duration_min"].fillna(
        NEARSHORE_REFERENCE_EFFORT_MIN
    )
    obs = obs[obs["effort_duration_min"].notna() & (obs["effort_duration_min"] > 0)].copy()
    if obs.empty:
        raise SystemExit("no eligible rows after biology/effort QC")

    # Encounter-only: binary 0/1 (Poisson-link delta encounter component; not biomass).
    counts = pd.DataFrame(
        {
            "event_id": obs["event_id"].astype(str),
            "taxon": TAXON,
            "count": obs["encounter"].astype(int).clip(0, 1).astype(float),
        }
    )
    event_ids = sorted(counts["event_id"].unique())
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
    cov = (
        obs.drop_duplicates(subset=["event_id"], keep="first")
        .loc[:, [c for c in cov_cols if c in obs.columns]]
        .sort_values("event_id")
        .reset_index(drop=True)
    )
    drops_out = out_dir / f"adult_cps_covariate_drops_{TAXON}.parquet"
    drop_summary_out = out_dir / f"adult_cps_covariate_drop_summary_{TAXON}.json"
    drops_out.parent.mkdir(parents=True, exist_ok=True)
    # Model-ready cov/counts are pre-filtered to !excluded; R requires an empty drop
    # table when no cov rows carry excluded=TRUE (same contract as adult CPS export).
    pd.DataFrame(
        columns=["event_id", "reason", "covariate", "latitude", "longitude"]
    ).to_parquet(drops_out, index=False)
    drop_summary_out.write_text(
        json.dumps(
            {
                "dropped_unique_total": 0,
                "input_event_count": int(len(cov)),
                "unique_by_reason": {},
                "rows_by_reason": {},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if set(cov["event_id"].astype(str)) != set(event_ids):
        raise SystemExit("covariate event_id set mismatch vs counts")

    out_dir.mkdir(parents=True, exist_ok=True)
    events_out = out_dir / f"adult_cps_events_{TAXON}.parquet"
    counts_out = out_dir / f"adult_cps_counts_{TAXON}.parquet"
    cov_out = out_dir / f"adult_cps_covariates_{TAXON}.parquet"
    events.to_parquet(events_out, index=False)
    counts.to_parquet(counts_out, index=False)
    cov.to_parquet(cov_out, index=False)

    pres = obs[obs["encounter"] == 1]
    by_source = {}
    for src, sub in pres.groupby("observation_source"):
        by_source[str(src)] = {
            "presence_rows": int(len(sub)),
            "presence_unique_events": int(sub["event_id"].nunique()),
        }

    summary = {
        "product_label": (
            "market squid encounter probability (all sizes; maturity unfiltered)"
        ),
        "encounter_semantics": ENCOUNTER_LABEL,
        "not_adult_model": True,
        "species": MARKET_SQUID_CANONICAL,
        "taxon": TAXON,
        "response": "encounter_only_binary_0_1",
        "n_physics_events": int(len(events_raw)),
        "n_model_events": int(len(events)),
        "n_observation_rows": int(len(obs)),
        "n_presence_rows": int((obs["encounter"] == 1).sum()),
        "n_presence_unique_events": int(pres["event_id"].nunique()),
        "n_absence_rows": int((obs["encounter"] == 0).sum()),
        "presence_by_source": by_source,
        "events_path": str(events_out),
        "counts_path": str(counts_out),
        "covariates_path": str(cov_out),
        "covariate_drops_path": str(drops_out),
        "covariate_drop_summary_path": str(drop_summary_out),
    }
    (out_dir / f"adult_cps_model_export_{TAXON}.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export market squid encounter model-ready parquet tables"
    )
    parser.add_argument("--events", type=Path, default=SQUID_EVENTS)
    parser.add_argument("--training-table", type=Path, default=SQUID_TABLE)
    parser.add_argument("--out-dir", type=Path, default=MODEL_DIR)
    args = parser.parse_args(argv)
    summary = export_model_tables(
        events_path=args.events,
        training_path=args.training_table,
        out_dir=args.out_dir,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
