#!/usr/bin/env python3
"""Sample issued WCOFS covariates for adult sardine 24h holdout rows (public PDS only)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

WCOFS_ARCHIVE_START = dt.date(2024, 7, 1)
DYN_Z_COLS = ("temp_3m_z", "sal_3m_z", "mld_z", "sst_grad_z", "dist_front_z")
UPSTREAM = {
    "temp_3m_z": "T3m",
    "sal_3m_z": "S3m",
    "mld_z": "MLD_m",
    "sst_grad_z": "sst_grad",
    "dist_front_z": "front_distance_km",
}


def _nearest_cell(lat: float, lon: float, lat_axis: np.ndarray, lon_axis: np.ndarray) -> tuple[int, int]:
    from fishai.ingestion.physics.cufes_training_covariates import normalize_lon_for_axis

    lon = normalize_lon_for_axis(lon, lon_axis)
    j = int(np.argmin(np.abs(lat_axis - lat)))
    i = int(np.argmin(np.abs(lon_axis - lon)))
    return j, i


def _event_lat_lon(row: pd.Series) -> tuple[float, float]:
    lat0, lon0 = float(row["lat"]), float(row["lon"])
    lat1 = row.get("stop_lat")
    lon1 = row.get("stop_lon")
    if pd.notna(lat1) and pd.notna(lon1):
        return (lat0 + float(lat1)) / 2.0, (lon0 + float(lon1)) / 2.0
    return lat0, lon0


def _resolve_lead(cutoff: dt.date, h_days: int, cycle_exists) -> tuple[dt.date, str, str | None]:
    from fishai.ingestion.physics.sources import wcofs as wcofs_src
    from fishai.ingestion.physics.wcofs_daily import resolve_lead_for_offset

    offset_h = h_days * 24
    tag = f"f{offset_h:03d}"
    if tag not in wcofs_src.FORECAST_LEADS:
        return cutoff, tag, "lead_out_of_range"
    if cycle_exists(cutoff):
        return cutoff, tag, None
    lp = resolve_lead_for_offset(
        cutoff,
        offset_h,
        primary_available=False,
        cycle_exists_fn=cycle_exists,
        max_missed_cycles=5,
    )
    if lp is None:
        return cutoff, tag, "missing_operational_cycle"
    return lp.cycle_date, lp.lead_tag, lp.fallback


def _fetch_wcofs_fields(cycle: dt.date, lead: str, bbox: tuple[float, float, float, float]):
    from fishai.ingestion.physics.sources import wcofs as wcofs_src
    from fishai.ingestion.physics.wcofs_pds_store import CycleNotAvailable, open_wcofs_cycle

    try:
        ds = open_wcofs_cycle(cycle, product="fields", lead=lead)
    except CycleNotAvailable:
        return None, None
    ds = wcofs_src.subset_bbox(ds, bbox)
    key = str(ds.attrs.get("wcofs_s3_key", wcofs_src.fields_s3_key(cycle, lead)))
    return ds, key


def _sample_covariates(ds, lat: float, lon: float, config: dict) -> dict[str, float] | None:
    from fishai.ingestion.physics.wcofs_glorys_grid import (
        coarsen_wcofs_to_glorys,
        compute_wcofs_covariates_on_glorys_grid,
    )
    from fishai.ingestion.physics.wcofs_glorys_grid import min_wet_fraction_from_config
    from fishai.ingestion.physics.wcofs_glorys_overlap import glorys_grid_from_config

    lat_dst, lon_dst = glorys_grid_from_config(config)
    gridded = coarsen_wcofs_to_glorys(
        ds,
        lat_dst,
        lon_dst,
        min_wet_fraction=min_wet_fraction_from_config(config),
    )
    fields = compute_wcofs_covariates_on_glorys_grid(gridded)
    j, i = _nearest_cell(lat, lon, lat_dst, lon_dst)
    out: dict[str, float] = {}
    for z_col, raw in UPSTREAM.items():
        arr = fields[raw]
        val = float(arr[j, i])
        if not np.isfinite(val):
            return None
        out[z_col] = val
    return out


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
    from fishai.ingestion.physics.wcofs_pds_store import cycle_available
    from fishai.ingestion.sources import load_sources_manifest

    parser = argparse.ArgumentParser(description="WCOFS operational covariates for adult sardine 24h holdout")
    parser.add_argument("--cutoffs-json", required=True, help="JSON with cutoffs list (YYYY-MM-DD)")
    parser.add_argument(
        "--training-table",
        default=str(REPO_ROOT / "data/processed/adult_cps/adult_cps_training_table.parquet"),
    )
    parser.add_argument(
        "--events-table",
        default=str(REPO_ROOT / "data/processed/adult_cps/adult_cps_events.parquet"),
    )
    parser.add_argument(
        "--scientific-name",
        default="Sardinops sagax",
        help="Species filter (must match adult_cps_sardine.yaml)",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    with Path(args.cutoffs_json).open(encoding="utf-8") as handle:
        cutoffs = [dt.date.fromisoformat(c) for c in json.load(handle)["cutoffs"]]

    train = pd.read_parquet(args.training_table)
    train = train[train["species"] == args.scientific_name].copy()
    events = pd.read_parquet(args.events_table)
    ev_cols = [c for c in ("event_id", "lat", "lon", "stop_lat", "stop_lon", "time") if c in events.columns]
    train = train.merge(events[ev_cols], on="event_id", how="left")
    origin = dt.date(1990, 1, 1)
    train["event_day"] = origin + pd.to_timedelta(train["time_idx"].astype(int) - 1, unit="D")

    manifest = load_sources_manifest()
    pilot = manifest.get("pilot") or {}
    box = pilot.get("bbox") or {}
    bbox = (float(box["lat_min"]), float(box["lat_max"]), float(box["lon_min"]), float(box["lon_max"]))
    config = load_overlap_config()

    rows: list[dict] = []
    for cutoff in cutoffs:
        hold = train[train["event_day"].isin([cutoff + dt.timedelta(days=h) for h in (1, 2, 3)])]
        for _, ev in hold.iterrows():
            h_days = int((ev["event_day"] - cutoff).days)
            lat, lon = _event_lat_lon(ev)
            base = {
                "cutoff": cutoff.isoformat(),
                "event_id": ev["event_id"],
                "event_day": ev["event_day"].isoformat(),
                "horizon_days": h_days,
                "lat": lat,
                "lon": lon,
            }
            if cutoff < WCOFS_ARCHIVE_START:
                rows.append(
                    {
                        **base,
                        "physics_source": "damped_anomaly_proxy",
                        "operational_claim": "NOT_ISSUED_FORECAST",
                        "proxy_reason": "coverage_forced_proxy",
                        "wcofs_s3_key": "",
                        "wcofs_lead_tag": "",
                        **{c: np.nan for c in DYN_Z_COLS},
                    }
                )
                continue
            cycle, lead, fallback = _resolve_lead(cutoff, h_days, cycle_available)
            ds, key = _fetch_wcofs_fields(cycle, lead, bbox)
            if ds is None:
                rows.append(
                    {
                        **base,
                        "physics_source": "damped_anomaly_proxy",
                        "operational_claim": "NOT_ISSUED_FORECAST",
                        "proxy_reason": "missing_wcofs_object",
                        "wcofs_s3_key": "",
                        "wcofs_lead_tag": lead,
                        **{c: np.nan for c in DYN_Z_COLS},
                    }
                )
                continue
            sampled = _sample_covariates(ds, lat, lon, config)
            ds.close()
            if sampled is None:
                rows.append(
                    {
                        **base,
                        "physics_source": "damped_anomaly_proxy",
                        "operational_claim": "NOT_ISSUED_FORECAST",
                        "proxy_reason": "non_finite_wcofs_cell",
                        "wcofs_s3_key": key or "",
                        "wcofs_lead_tag": lead,
                        **{c: np.nan for c in DYN_Z_COLS},
                    }
                )
                continue
            rows.append(
                {
                    **base,
                    "physics_source": "wcofs_issued_forecast",
                    "operational_claim": "ISSUED_FORECAST",
                    "proxy_reason": fallback or "",
                    "wcofs_s3_key": key or "",
                    "wcofs_lead_tag": lead,
                    **sampled,
                }
            )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_path, index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
