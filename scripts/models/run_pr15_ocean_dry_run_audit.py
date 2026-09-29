#!/usr/bin/env python3
"""Build PR #15 (@ pin ref) CUFES ocean covariates and write dry-run QA report (read-only git pin)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
DEFAULT_PR15 = "794261bfb0cd86ce72145190a1b564ea85202865"
EVENTS = REPO / "data/processed/calcofi_cufes/cufes_events.parquet"
COUNTS = REPO / "data/processed/calcofi_cufes/cufes_counts.parquet"


def _ensure_worktree(ref: str, dest: Path) -> Path:
    if dest.is_dir() and (dest / "src/fishai/ingestion/physics/cufes_training_covariates.py").is_file():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(dest), ref],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    )
    return dest


def _normalize_events(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "time": "start_time",
        "lat": "start_latitude",
        "lon": "start_longitude",
        "stop_lat": "stop_latitude",
        "stop_lon": "stop_longitude",
    }
    out = df.copy()
    for old, new in rename.items():
        if old in out.columns and new not in out.columns:
            out = out.rename(columns={old: new})
    return out


def build_table(ref: str, out_dir: Path) -> tuple[Path, Path]:
    wt = _ensure_worktree(ref, Path(f"/tmp/pr15_worktree_{ref[:7]}"))
    sys.path.insert(0, str(wt / "src"))
    from fishai.ingestion.physics.cufes_training_covariates import (  # noqa: WPS433
        DEFAULT_DROPS_NAME,
        build_cufes_training_covariates_table,
        glorys_store_from_synthetic_days,
        unique_event_days,
        write_training_covariates_parquet,
    )

    events = _normalize_events(pd.read_parquet(EVENTS))
    if len(events) != 14592:
        raise SystemExit(f"expected 14592 kept events, got {len(events)}")
    days = unique_event_days(events)
    store = glorys_store_from_synthetic_days(days)
    out_dir.mkdir(parents=True, exist_ok=True)
    cov_path = out_dir / "cufes_training_covariates.parquet"
    drops_path = out_dir / DEFAULT_DROPS_NAME
    summary_path = out_dir / "cufes_training_covariate_drop_summary.json"
    table, qc, drops, floor_qc = build_cufes_training_covariates_table(
        events,
        store,
        provenance=f"pr15@{ref[:7]} dry_run",
        drops_parquet_path=drops_path,
        drop_summary_json_path=summary_path,
    )
    write_training_covariates_parquet(table, cov_path, entry={}, store=store)
    meta = {
        "pr15_ref": ref,
        "pr15_pull": "https://github.com/wijeratne-a/fishai/pull/15",
        "qc": qc,
        "floor_qc": floor_qc,
        "row_count": int(len(table)),
    }
    (out_dir / "build_meta.json").write_text(json.dumps(meta, indent=2, default=str) + "\n")
    return cov_path, drops_path


def audit(out_dir: Path, ref: str) -> dict:
    sys.path.insert(0, str(REPO / "src"))
    from fishai.models.bot2_covariate_schema import compare_bot2_to_sdmtmb, mismatches_as_dicts

    cov = pd.read_parquet(out_dir / "cufes_training_covariates.parquet")
    events = pd.read_parquet(EVENTS)
    counts = pd.read_parquet(COUNTS)
    drops = pd.read_parquet(out_dir / "cufes_training_covariate_drops.parquet")

    fit_end = pd.Timestamp("2017-12-31", tz="UTC")
    test_start = pd.Timestamp("2018-01-01", tz="UTC")
    test_end = pd.Timestamp("2022-04-27", tz="UTC")

    excluded = cov["excluded"].astype(str).str.upper().isin({"TRUE", "1", "T", "YES"}) | cov[
        "excluded"
    ].eq(True)
    kept = cov[~excluded]

    def species_stats(taxon: str) -> dict:
        ct = counts[counts["taxon"] == taxon]
        merged = events.merge(ct[["event_id", "count"]], on="event_id", how="inner")
        merged["time"] = pd.to_datetime(merged["time"], utc=True)
        pos = merged["count"] > 0
        fit = merged[merged["time"] <= fit_end]
        test = merged[(merged["time"] >= test_start) & (merged["time"] <= test_end)]
        test_spring = test[pos & test["time"].dt.month.isin([3, 4, 5, 6])]
        by_year = test_spring.groupby(test_spring["time"].dt.year)["event_id"].nunique()
        return {
            "n_fit_positives": int((fit["count"] > 0).sum()),
            "n_test_positives": int((test["count"] > 0).sum()),
            "test_springs_with_positive": int((by_year > 0).sum()),
            "test_spring_positive_events": int(len(test_spring)),
        }

    physics = ["T3m", "S3m", "MLD_m", "sst_grad", "front_distance_km"]
    report = {
        "pr15_ref": ref,
        "pr15_pull": "https://github.com/wijeratne-a/fishai/pull/15",
        "not_merged": True,
        "n_events": 14592,
        "n_covariate_rows": int(len(cov)),
        "all_event_ids_present": set(cov.event_id) == set(events.event_id),
        "excluded_rows": int(excluded.sum()),
        "bottom_depth_m_positive_on_kept": bool((kept["bottom_depth_m"] > 0).all()),
        "nan_physics_on_kept": {c: int(kept[c].isna().sum()) for c in physics},
        "drops_by_reason": dict(Counter(drops["reason"].astype(str))),
        "excluded_reason_counts": cov.loc[excluded, "excluded_reason"].value_counts().to_dict(),
        "species": {"sardine": species_stats("sardine"), "anchovy": species_stats("anchovy")},
        "schema_mismatches_pr5_vs_pr15": mismatches_as_dicts(compare_bot2_to_sdmtmb(ref=ref)),
        "events_column_bridge_note": (
            "#5 cufes_events.parquet uses time/lat/lon; PR #15 builder expects start_time/start_latitude/… "
            "(renamed in this harness only)"
        ),
        "build_note": (
            "At pin 794261b, run_build fills GLORYS fields via glorys_store_from_synthetic_days after optional "
            "Copernicus subset; no Copernicus cache in this VM — table shape/metadata from PR #15 code path, "
            "not live CMEMS values."
        ),
    }
    if "upwelling" not in cov.columns:
        report["upwelling"] = "absent_column"
    elif kept["upwelling"].isna().all():
        report["upwelling"] = "blank_on_kept"
    else:
        report["upwelling"] = "present_on_kept"
    path = out_dir / "pr15_dry_run_audit_report.json"
    path.write_text(json.dumps(report, indent=2, default=str) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", default=DEFAULT_PR15)
    parser.add_argument("--out-dir", type=Path, default=Path("/tmp/pr15_dry_run_794261b"))
    args = parser.parse_args()
    build_table(args.ref, args.out_dir)
    report = audit(args.out_dir, args.ref)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
