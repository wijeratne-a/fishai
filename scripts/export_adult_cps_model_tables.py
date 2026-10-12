#!/usr/bin/env python3
"""Export R model-ready events / counts / covariates from adult CPS training outputs."""

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
    DEFAULT_DROPS_PATH,
    DEFAULT_DROP_SUMMARY_PATH,
    DEFAULT_EVENTS_PATH,
    DEFAULT_PROCESSED_DIR,
    DEFAULT_TRAINING_TABLE_PATH,
)
from fishai.ingestion.physics.cufes_training_covariates import TRAINING_OUTPUT_COLUMNS  # noqa: E402

ANCHOVY_SPECIES = "Engraulis mordax"
TAXON = "anchovy"
MODEL_DIR = DEFAULT_PROCESSED_DIR / "model_ready"
# Purse-seine nearshore sets have no tow duration; Poisson offset uses log(1 min) = 0.
NEARSHORE_REFERENCE_EFFORT_MIN = 2.0
NEARSHORE_SOURCE = "swfsc_cps_nearshore_set_catch"


def _positive_biomass(row: pd.Series) -> float:
    enc = int(row["encounter"])
    if enc <= 0:
        return 0.0
    weight = row.get("weight_kg")
    if weight is not None and pd.notna(weight) and float(weight) > 0:
        return float(weight)
    count = row.get("count_observed")
    if count is not None and pd.notna(count) and int(count) > 0:
        return float(int(count))
    return 1.0


def _events_for_r(events: pd.DataFrame) -> pd.DataFrame:
    """Map physics events to the cufes_events columns the R loader validates."""
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
            # Schema placeholders (effort for delta model uses effort_duration_min).
            "volume_m3": events["effort_duration_min"].astype(float),
            "pump_readings_used": 1,
            "short_event": False,
        }
    )
    return out


def export_model_tables(
    *,
    species: str = ANCHOVY_SPECIES,
    taxon: str = TAXON,
    events_path: Path = DEFAULT_EVENTS_PATH,
    training_path: Path = DEFAULT_TRAINING_TABLE_PATH,
    out_dir: Path = MODEL_DIR,
) -> dict[str, object]:
    events_raw = pd.read_parquet(events_path)
    table = pd.read_parquet(training_path)
    obs = table[table["species"] == species].copy()
    if obs.empty:
        raise SystemExit(f"no training rows for species={species!r}")
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
            "taxon": taxon,
            "count": obs.apply(_positive_biomass, axis=1),
        }
    )
    event_ids = sorted(counts["event_id"].unique())
    # Full physics-event frame for spatial-block assignment; counts restrict the fit rows.
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
    drops_out = out_dir / f"adult_cps_covariate_drops_{taxon}.parquet"
    drop_summary_out = out_dir / f"adult_cps_covariate_drop_summary_{taxon}.json"
    drops_out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=pd.read_parquet(DEFAULT_DROPS_PATH).columns).to_parquet(
        drops_out, index=False
    )
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
    events_out = out_dir / f"adult_cps_events_{taxon}.parquet"
    counts_out = out_dir / f"adult_cps_counts_{taxon}.parquet"
    cov_out = out_dir / f"adult_cps_covariates_{taxon}.parquet"
    events.to_parquet(events_out, index=False)
    counts.to_parquet(counts_out, index=False)
    cov.to_parquet(cov_out, index=False)

    summary = {
        "species": species,
        "taxon": taxon,
        "n_physics_events": int(len(events_raw)),
        "n_model_events": int(len(events)),
        "n_observation_rows": int(len(obs)),
        "n_presence": int((obs["encounter"] == 1).sum()),
        "n_absence": int((obs["encounter"] == 0).sum()),
        "events_path": str(events_out),
        "counts_path": str(counts_out),
        "covariates_path": str(cov_out),
        "covariate_drops_path": str(drops_out),
        "covariate_drop_summary_path": str(drop_summary_out),
    }
    (out_dir / f"adult_cps_model_export_{taxon}.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export adult CPS model-ready parquet tables")
    parser.add_argument("--taxon", default=TAXON)
    parser.add_argument("--species", default=ANCHOVY_SPECIES)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS_PATH)
    parser.add_argument("--training-table", type=Path, default=DEFAULT_TRAINING_TABLE_PATH)
    parser.add_argument("--out-dir", type=Path, default=MODEL_DIR)
    args = parser.parse_args(argv)
    summary = export_model_tables(
        species=args.species,
        taxon=args.taxon,
        events_path=args.events,
        training_path=args.training_table,
        out_dir=args.out_dir,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
