#!/usr/bin/env python3
"""Build a common SCB 10 km prediction grid with GLORYS covariates for coherence maps."""

from __future__ import annotations

import argparse
import math
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from fishai.ingestion.physics.covariates import CUFES_COVARIATE_FIELDS  # noqa: E402
from fishai.ingestion.physics.cufes_training_covariates import (  # noqa: E402
    GlorysFieldStore,
    load_events_parquet,
    new_glorys_field_store_for_live_build,
    populate_store_days_from_cache,
    unique_event_days,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config  # noqa: E402
from fishai.ingestion.sources import REPO_ROOT as REPO  # noqa: E402


def _utm_km(lat: float, lon: float, epsg: int = 32611) -> tuple[float, float]:
    from pyproj import Transformer

    transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    x_m, y_m = transformer.transform(lon, lat)
    return x_m / 1000.0, y_m / 1000.0


def build_cell_centers(
    *,
    lat_min: float = 32.0,
    lat_max: float = 35.0,
    lon_min: float = -121.0,
    lon_max: float = -117.0,
    spacing_km: float = 10.0,
) -> pd.DataFrame:
    lat_c = 0.5 * (lat_min + lat_max)
    dlat = spacing_km / 111.0
    dlon = spacing_km / (111.0 * max(math.cos(math.radians(lat_c)), 1e-6))
    lats = np.arange(lat_min + dlat / 2.0, lat_max, dlat)
    lons = np.arange(lon_min + dlon / 2.0, lon_max, dlon)
    rows: list[dict[str, float]] = []
    for la in lats:
        for lo in lons:
            x_km, y_km = _utm_km(float(la), float(lo))
            rows.append(
                {
                    "latitude": float(la),
                    "longitude": float(lo),
                    "X": x_km,
                    "Y": y_km,
                    "cell_id": f"g{math.floor(x_km / 10)}_{math.floor(y_km / 10)}",
                }
            )
    return pd.DataFrame(rows)


def _parse_subset_nc_dates(path: Path) -> tuple[date, date]:
    """Parse ``{dataset_id}_{start}_{end}.nc`` date span from cache filename."""
    stem = path.stem
    end = date.fromisoformat(stem.rsplit("_", 1)[-1])
    start = date.fromisoformat(stem.rsplit("_", 2)[-2])
    return start, end


def _batches_from_glorys_cache(days: list[date], cache_dir: Path) -> list:
    from fishai.ingestion.physics.cufes_training_covariates import (
        GlorysSubsetBatch,
        PILOT_BBOX,
        TRAINING_SUBSET_VARIABLES,
    )
    from fishai.ingestion.physics.sources.glorys import glorys_product_for_date

    nc_files = sorted(cache_dir.glob("*.nc"))
    if not nc_files:
        raise FileNotFoundError(f"no GLORYS subset cache under {cache_dir}")
    by_key: dict[tuple[str, date, date], Path] = {}
    for nc in nc_files:
        start, end = _parse_subset_nc_dates(nc)
        dataset_id = nc.name.rsplit("_", 2)[0]
        by_key[(dataset_id, start, end)] = nc

    batches: list[GlorysSubsetBatch] = []
    seen: set[tuple[str, date, date]] = set()
    for day in days:
        product_id = glorys_product_for_date(day)
        hit = None
        for (dataset_id, start, end), _path in by_key.items():
            if dataset_id != product_id:
                continue
            if start <= day <= end:
                hit = (dataset_id, start, end)
                break
        if hit is None:
            raise FileNotFoundError(f"no cached GLORYS subset covers {day.isoformat()}")
        if hit not in seen:
            seen.add(hit)
            dataset_id, start, end = hit
            batches.append(
                GlorysSubsetBatch(
                    dataset_id=dataset_id,
                    date_start=start,
                    date_end=end,
                    variables=TRAINING_SUBSET_VARIABLES,
                    bbox=PILOT_BBOX,
                )
            )
    return batches


def _load_glorys_store_for_days(days: list[date]) -> GlorysFieldStore:
    cfg = load_overlap_config()
    store = new_glorys_field_store_for_live_build(cfg)
    cache_dir = REPO / "data" / "cache" / "glorys_cufes"
    if not cache_dir.is_dir():
        raise FileNotFoundError(
            f"GLORYS cache missing at {cache_dir}; run CUFES×GLORYS training covariate build first"
        )
    batches = _batches_from_glorys_cache(days, cache_dir)
    populate_store_days_from_cache(store, days, batches, cache_dir)
    return store


def grid_with_covariates(
    grid: pd.DataFrame,
    *,
    when: datetime,
    store: GlorysFieldStore,
) -> pd.DataFrame:
    ts = pd.Timestamp(when)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    sampler = store.field_sampler
    out_rows: list[dict[str, object]] = []
    for _, row in grid.iterrows():
        sampled = sampler(float(row["latitude"]), float(row["longitude"]), ts)
        depth, _reason = store.sample_bottom_depth_with_reason(float(row["latitude"]), float(row["longitude"]))
        rec = dict(row)
        for field in CUFES_COVARIATE_FIELDS:
            rec[field] = sampled.get(field, np.nan)
        rec["bottom_depth_m"] = depth
        if depth and depth > 0:
            rec["log_depth"] = float(np.log(depth))
        else:
            rec["log_depth"] = np.nan
        out_rows.append(rec)
    return pd.DataFrame(out_rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SCB 10 km coherence prediction grid")
    parser.add_argument("--day", type=str, required=True, help="UTC calendar day YYYY-MM-DD")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "artifacts" / "coherence" / "scb_10km_grid.csv",
    )
    parser.add_argument(
        "--events",
        type=Path,
        default=REPO_ROOT / "data" / "processed" / "calcofi_cufes" / "cufes_events.parquet",
        help="Used only to verify GLORYS cache covers event days",
    )
    args = parser.parse_args(argv)

    day = date.fromisoformat(args.day)
    grid = build_cell_centers()
    days = [day]
    if args.events.is_file():
        ev_days = unique_event_days(load_events_parquet(args.events))
        if day not in ev_days:
            # still allow arbitrary climatology days
            pass
    store = _load_glorys_store_for_days(days)
    enriched = grid_with_covariates(grid, when=datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc), store=store)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(args.output, index=False)
    print(f"wrote {args.output} rows={len(enriched)} day={day.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
