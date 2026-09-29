"""Build bot2-shaped covariate tables for PR #5 dry-run integration (temp only)."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import pandas as pd

from fishai.ingestion.physics.sources.glorys import glorys_product_for_date
from fishai.models.bot2_expected_contract import (
    PLANNED_COVARIATE_GAPS,
    SYNTHETIC_FIXTURE_NOTE,
    harness_run_metadata,
    training_output_columns_for_mode,
)

REPO = Path(__file__).resolve().parents[2]
EVENTS_FIXTURE = REPO / "src" / "models" / "tests" / "fixtures" / "synthetic_cufes_events.csv"
COUNTS_FIXTURE = REPO / "src" / "models" / "tests" / "fixtures" / "synthetic_cufes_counts.csv"
COV_FIXTURE = REPO / "src" / "models" / "tests" / "fixtures" / "synthetic_cufes_covariates.csv"
EXPECTED_CONTRACT_COV = (
    REPO / "tests" / "models" / "fixtures" / "synthetic_expected_bot2_contract_covariates.csv"
)


def spring_subset_event_ids(*, max_events: int = 20) -> list[str]:
    """Small subset from synthetic fixtures (June pilot slice)."""
    rows = list(csv.DictReader(EVENTS_FIXTURE.open(encoding="utf-8")))
    return [row["event_id"] for row in rows[:max_events]]


def write_spring_subset_csvs(
    out_dir: Path,
    *,
    bot2_columns: tuple[str, ...] | None = None,
    schema_mode: str | None = None,
    planned_upwelling_gap: bool = True,
) -> dict[str, Path]:
    """Write temp CSVs for dry-run harness (SYNTHETIC subset).

    Covariates follow the expected bot2 contract when ``schema_mode`` is ``expected``
    or when the bot2 git branch is unavailable (``BOT2_SCHEMA_MODE=auto``).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = harness_run_metadata(mode=schema_mode)
    resolved_mode = str(meta["mode"])
    bot2_columns = bot2_columns or training_output_columns_for_mode(mode=resolved_mode)
    ids = set(spring_subset_event_ids())

    ev_rows = [r for r in csv.DictReader(EVENTS_FIXTURE.open(encoding="utf-8")) if r["event_id"] in ids]
    ct_rows = [r for r in csv.DictReader(COUNTS_FIXTURE.open(encoding="utf-8")) if r["event_id"] in ids]
    cov_rows = [r for r in csv.DictReader(COV_FIXTURE.open(encoding="utf-8")) if r["event_id"] in ids]

    events_path = out_dir / "cufes_events_spring_subset.csv"
    counts_path = out_dir / "cufes_counts_spring_subset.csv"
    cov_path = out_dir / "cufes_training_covariates_spring_subset.csv"
    meta_path = out_dir / "bot2_harness_schema_meta.json"

    with events_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ev_rows[0].keys())
        writer.writeheader()
        writer.writerows(ev_rows)

    with counts_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["event_id", "taxon", "count"])
        writer.writeheader()
        writer.writerows(ct_rows)

    upwelling_gap_reason = PLANNED_COVARIATE_GAPS["upwelling"]
    bot2_rows: list[dict[str, object]] = []
    for row in cov_rows:
        ev = next(e for e in ev_rows if e["event_id"] == row["event_id"])
        iso_day = ev["time"][:10]
        product = glorys_product_for_date(
            __import__("datetime").date.fromisoformat(iso_day)
        )
        depth_m = 120.0
        excluded = row["excluded"] == "TRUE"
        if planned_upwelling_gap and not excluded:
            upwelling_val: object = ""
            upwelling_status = upwelling_gap_reason
        else:
            upwelling_val = (
                float(row["upwelling"]) if row["upwelling"] not in ("", "NaN") else float("nan")
            )
            upwelling_status = "ok"
        rec: dict[str, object] = {
            "event_id": row["event_id"],
            "T3m": float(row["T3m"]) if row["T3m"] not in ("", "NaN") else float("nan"),
            "S3m": float(row["S3m"]) if row["S3m"] not in ("", "NaN") else float("nan"),
            "MLD_m": float(row["MLD_m"]) if row["MLD_m"] not in ("", "NaN") else float("nan"),
            "sst_grad": float(row["sst_grad"]) if row["sst_grad"] not in ("", "NaN") else float("nan"),
            "front_distance_km": float(row["front_distance_km"])
            if row["front_distance_km"] not in ("", "NaN")
            else float("nan"),
            "upwelling": upwelling_val,
            "upwelling_status": upwelling_status,
            "bottom_depth_m": depth_m,
            "depth_at_model_floor": False,
            "source": "glorys",
            "provenance": "dry_run_synthetic_expected_contract",
            "excluded": row["excluded"],
            "source_product": product,
            "excluded_reason": "" if row["excluded"] == "FALSE" else "missing_covariate",
        }
        bot2_rows.append(rec)

    frame = pd.DataFrame(bot2_rows)
    for col in bot2_columns:
        if col not in frame.columns:
            frame[col] = pd.NA
    frame = frame[list(bot2_columns)]
    frame.to_csv(cov_path, index=False)

    import json

    meta_path.write_text(
        json.dumps(
            {
                **meta,
                "schema_mode_env": os.environ.get("BOT2_SCHEMA_MODE", "auto"),
                "synthetic_note": SYNTHETIC_FIXTURE_NOTE,
                "planned_upwelling_gap": planned_upwelling_gap,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "events": events_path,
        "counts": counts_path,
        "covariates": cov_path,
        "schema_meta": meta_path,
        "mode": resolved_mode,
        "branch_existed": bool(meta["branch_existed"]),
    }


def write_minimal_expected_contract_csvs(out_dir: Path) -> dict[str, Path]:
    """Three-row SYNTHETIC table matching the documented expected bot2 contract."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ids = ["CUFES:SYN:AK:001", "CUFES:SYN:AK:002", "CUFES:SYN:AK:003"]
    ev_rows = [r for r in csv.DictReader(EVENTS_FIXTURE.open(encoding="utf-8")) if r["event_id"] in ids]
    if len(ev_rows) < 3:
        ev_rows = []
        for i, eid in enumerate(ids, start=1):
            ev_rows.append(
                {
                    "event_id": eid,
                    "time": f"2020-06-0{i}T12:00:00Z",
                    "lat": "33.0",
                    "lon": "-119.0",
                    "stop_time": f"2020-06-0{i}T12:10:00Z",
                    "stop_lat": "33.01",
                    "stop_lon": "-118.99",
                    "volume_m3": "10",
                    "pump_readings_used": "2",
                    "duration_min": "10",
                    "short_event": "FALSE",
                    "time_idx": str(i),
                }
            )
    ct_rows = [{"event_id": eid, "taxon": "sardine", "count": "1"} for eid in ids]
    events_path = out_dir / "cufes_events_minimal_synthetic.csv"
    counts_path = out_dir / "cufes_counts_minimal_synthetic.csv"
    cov_path = out_dir / "cufes_covariates_minimal_synthetic.csv"
    with events_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ev_rows[0].keys())
        writer.writeheader()
        writer.writerows(ev_rows[:3])
    with counts_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["event_id", "taxon", "count"])
        writer.writeheader()
        writer.writerows(ct_rows)
    cov_dest = out_dir / "cufes_covariates_minimal_synthetic.csv"
    cov_dest.write_text(EXPECTED_CONTRACT_COV.read_text(encoding="utf-8"), encoding="utf-8")
    meta = harness_run_metadata(mode="expected")
    return {
        "events": events_path,
        "counts": counts_path,
        "covariates": cov_dest,
        "mode": "expected",
        "branch_existed": bool(meta["branch_existed"]),
    }
