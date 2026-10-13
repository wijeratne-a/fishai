#!/usr/bin/env python3
"""Join PacFIN public shoreside CPS catch (port-group × year) to adult CPS events.

Source: PacFIN ALL005 via CPS SAFE Portal (California agency, 2003–2025).
See docs/jack-mackerel-catch-proxy-readout.md for bias-correction assumptions.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]

PORT_GROUPS = ("SDA", "LAA", "SBA", "MNA", "MRA", "SFA", "BDA", "BGA", "ERA", "CCA")
CPS_WETF_CODES = ("JMCK", "PSDN", "NANC", "MSQD", "CMCK", "UMCK")

# Offshore lat bands for SCB pilot (32–35°N); coarse PacFIN port-complex proxy at sea.
PORT_LAT_BREAKS: tuple[tuple[float, float, str], ...] = (
    (32.0, 33.17, "SDA"),
    (33.17, 34.45, "LAA"),
    (34.45, 35.01, "SBA"),
    (35.01, 36.5, "MNA"),
)


def assign_port_group(lat: float) -> str:
    for lo, hi, code in PORT_LAT_BREAKS:
        if lo <= lat < hi:
            return code
    return "MNA"


def _parse_mt(val: object) -> float:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 0.0
    s = str(val).strip()
    if not s or s == "*":
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def load_pacfin_port_year(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype=str)
    raw["LANDING_YEAR"] = raw["LANDING_YEAR"].astype(int)
    rows: list[dict] = []
    for _, r in raw.iterrows():
        if r.get("MANAGEMENT_GROUP_CODE") != "CPEL":
            continue
        code = r.get("PACFIN_SPECIES_CODE", "")
        year = int(r["LANDING_YEAR"])
        for pg in PORT_GROUPS:
            col = f"{pg}_LANDED_WEIGHT_MTONS"
            if col not in r.index:
                continue
            mt = _parse_mt(r[col])
            rows.append(
                {
                    "landing_year": year,
                    "port_group": pg,
                    "species_code": code,
                    "catch_weight_mt": mt,
                }
            )
    long = pd.DataFrame(rows)
    jmck = (
        long[long["species_code"] == "JMCK"]
        .groupby(["landing_year", "port_group"], as_index=False)["catch_weight_mt"]
        .sum()
        .rename(columns={"catch_weight_mt": "comm_catch_jmck_mt"})
    )
    cps = (
        long[long["species_code"].isin(CPS_WETF_CODES)]
        .groupby(["landing_year", "port_group"], as_index=False)["catch_weight_mt"]
        .sum()
        .rename(columns={"catch_weight_mt": "comm_fleet_effort_mt"})
    )
    return jmck.merge(cps, on=["landing_year", "port_group"], how="outer").fillna(0.0)


def attach_to_training_table(
    training_path: Path,
    pacfin_path: Path,
    out_path: Path,
    events_path: Path | None = None,
) -> dict:
    train = pd.read_parquet(training_path)
    port_year = load_pacfin_port_year(pacfin_path)
    if events_path and events_path.is_file():
        ev = pd.read_parquet(events_path)
        if "start_latitude" in ev.columns:
            ev = ev.rename(
                columns={
                    "start_latitude": "lat",
                    "start_longitude": "lon",
                    "start_time": "time",
                }
            )
        ev = ev[["event_id", "lat", "lon", "time"]]
        train = train.merge(ev, on="event_id", how="left", suffixes=("", "_ev"))
    if "lat" not in train.columns:
        raise SystemExit("training table missing lat; pass --events")
    train["landing_year"] = pd.to_datetime(train["time"], utc=True).dt.year
    train["port_group"] = train["lat"].map(lambda x: assign_port_group(float(x)))
    train = train.merge(
        port_year,
        left_on=["landing_year", "port_group"],
        right_on=["landing_year", "port_group"],
        how="left",
    )
    train["comm_catch_jmck_mt"] = train["comm_catch_jmck_mt"].fillna(0.0)
    train["comm_fleet_effort_mt"] = train["comm_fleet_effort_mt"].fillna(0.0)
    import numpy as np

    train["log_comm_catch_jmck"] = np.log1p(train["comm_catch_jmck_mt"])
    train["log_comm_fleet_effort"] = np.log1p(train["comm_fleet_effort_mt"])
    summary = {
        "n_rows": int(len(train)),
        "n_with_positive_jmck": int((train["comm_catch_jmck_mt"] > 0).sum()),
        "port_groups": train["port_group"].value_counts().to_dict(),
        "years": sorted(train["landing_year"].unique().tolist()),
        "pacfin_source": str(pacfin_path),
    }
    # Leave event geometry/timing to adult_cps_events.parquet (R loader merges folds).
    drop_cols = [
        c
        for c in (
            "lat",
            "lon",
            "time",
            "lat_ev",
            "lon_ev",
            "time_ev",
            "landing_year",
            "port_group",
        )
        if c in train.columns
    ]
    train = train.drop(columns=drop_cols, errors="ignore")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    train.to_parquet(out_path, index=False)
    (out_path.parent / "catch_covariate_join_summary.json").write_text(
        json.dumps(summary, indent=2)
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Attach PacFIN port-year catch covariates")
    parser.add_argument(
        "--pacfin-csv",
        type=Path,
        default=REPO_ROOT / "data/raw/pacfin/all005_ca_2003_2025.csv",
    )
    parser.add_argument(
        "--training-table",
        type=Path,
        default=REPO_ROOT / "data/processed/adult_cps/adult_cps_training_table.parquet",
    )
    parser.add_argument(
        "--events",
        type=Path,
        default=REPO_ROOT / "data/processed/adult_cps/adult_cps_events.parquet",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / "data/processed/commercial_catch/adult_cps_training_table_with_catch.parquet",
    )
    args = parser.parse_args(argv)
    if not args.pacfin_csv.is_file():
        print(f"missing PacFIN CSV: {args.pacfin_csv}", file=sys.stderr)
        return 1
    if not args.training_table.is_file():
        print(f"missing training table: {args.training_table}", file=sys.stderr)
        return 2
    summary = attach_to_training_table(
        args.training_table, args.pacfin_csv, args.output, args.events
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
