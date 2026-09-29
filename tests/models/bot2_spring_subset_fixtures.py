"""Build bot2-shaped covariate tables for PR #5 dry-run integration (temp only)."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from fishai.ingestion.physics.sources.glorys import glorys_product_for_date
from fishai.models.bot2_covariate_schema import bot2_training_output_columns

REPO = Path(__file__).resolve().parents[2]
EVENTS_FIXTURE = REPO / "src" / "models" / "tests" / "fixtures" / "synthetic_cufes_events.csv"
COUNTS_FIXTURE = REPO / "src" / "models" / "tests" / "fixtures" / "synthetic_cufes_counts.csv"
COV_FIXTURE = REPO / "src" / "models" / "tests" / "fixtures" / "synthetic_cufes_covariates.csv"


def spring_subset_event_ids(*, max_events: int = 20) -> list[str]:
    """Small subset from synthetic fixtures (June pilot slice)."""
    rows = list(csv.DictReader(EVENTS_FIXTURE.open(encoding="utf-8")))
    return [row["event_id"] for row in rows[:max_events]]


def write_spring_subset_csvs(
    out_dir: Path,
    *,
    bot2_columns: tuple[str, ...] | None = None,
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ids = set(spring_subset_event_ids())
    bot2_columns = bot2_columns or bot2_training_output_columns()

    ev_rows = [r for r in csv.DictReader(EVENTS_FIXTURE.open(encoding="utf-8")) if r["event_id"] in ids]
    ct_rows = [r for r in csv.DictReader(COUNTS_FIXTURE.open(encoding="utf-8")) if r["event_id"] in ids]
    cov_rows = [r for r in csv.DictReader(COV_FIXTURE.open(encoding="utf-8")) if r["event_id"] in ids]
    ev_rows = [r for r in ev_rows if r["event_id"] in ids]
    ct_rows = [r for r in ct_rows if r["event_id"] in ids]

    events_path = out_dir / "cufes_events_spring_subset.csv"
    counts_path = out_dir / "cufes_counts_spring_subset.csv"
    cov_path = out_dir / "cufes_training_covariates_spring_subset.csv"

    with events_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ev_rows[0].keys())
        writer.writeheader()
        writer.writerows(ev_rows)

    with counts_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["event_id", "taxon", "count"])
        writer.writeheader()
        writer.writerows(ct_rows)

    bot2_rows: list[dict[str, object]] = []
    for row in cov_rows:
        day = row["event_id"]  # placeholder; use event time from ev_rows
        ev = next(e for e in ev_rows if e["event_id"] == row["event_id"])
        iso_day = ev["time"][:10]
        product = glorys_product_for_date(
            __import__("datetime").date.fromisoformat(iso_day)
        )
        depth_m = 120.0
        rec: dict[str, object] = {
            "event_id": row["event_id"],
            "T3m": float(row["T3m"]) if row["T3m"] not in ("", "NaN") else float("nan"),
            "S3m": float(row["S3m"]) if row["S3m"] not in ("", "NaN") else float("nan"),
            "MLD_m": float(row["MLD_m"]) if row["MLD_m"] not in ("", "NaN") else float("nan"),
            "sst_grad": float(row["sst_grad"]) if row["sst_grad"] not in ("", "NaN") else float("nan"),
            "front_distance_km": float(row["front_distance_km"])
            if row["front_distance_km"] not in ("", "NaN")
            else float("nan"),
            "upwelling": float(row["upwelling"]) if row["upwelling"] not in ("", "NaN") else float("nan"),
            "upwelling_status": "ok",
            "bottom_depth_m": depth_m,
            "depth_at_model_floor": False,
            "source": "glorys",
            "provenance": "dry_run_synthetic",
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

    return {
        "events": events_path,
        "counts": counts_path,
        "covariates": cov_path,
    }
