#!/usr/bin/env python3
"""24 h advection–taxis hindcast for jack mackerel encounter SDM (public GLORYS currents)."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from scipy.optimize import brute
from sklearn.metrics import roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from fishai.evaluation.advection_sdm import (  # noqa: E402
    AdvectionGrid,
    advection_at_point,
    persistence_at_point,
)
from fishai.evaluation.engine.metrics import brier_score  # noqa: E402
from fishai.ingestion.physics.covariates import CUFES_COVARIATE_FIELDS  # noqa: E402
from fishai.ingestion.physics.cufes_training_covariates import (  # noqa: E402
    GlorysFieldStore,
    GlorysSubsetBatch,
    PILOT_BBOX,
    new_glorys_field_store_for_live_build,
    plan_glorys_subset_batches,
    populate_store_days_from_cache,
)
from fishai.ingestion.physics.glorys_cufes_subset import TRAINING_SUBSET_VARIABLES  # noqa: E402
from fishai.ingestion.physics.sources.glorys import glorys_product_for_date  # noqa: E402
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config  # noqa: E402
from fishai.ingestion.sources import REPO_ROOT as REPO  # noqa: E402

OUT_DIR = REPO / "artifacts" / "models" / "jack_mackerel_advection_sdm"
GLORYS_ADULT_CACHE = REPO / "data" / "cache" / "glorys_adult_cps"
CURRENT_CACHE = REPO / "data" / "cache" / "glorys_advection_currents"


def _utm_km(lat: float, lon: float) -> tuple[float, float]:
    from pyproj import Transformer

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32611", always_xy=True)
    x_m, y_m = transformer.transform(lon, lat)
    return x_m / 1000.0, y_m / 1000.0


def build_grid_centers() -> pd.DataFrame:
    lat_min, lat_max, lon_min, lon_max = 32.0, 35.0, -121.0, -117.0
    spacing_km = 10.0
    lat_c = 0.5 * (lat_min + lat_max)
    dlat = spacing_km / 111.0
    dlon = spacing_km / (111.0 * max(math.cos(math.radians(lat_c)), 1e-6))
    rows: list[dict[str, float | str]] = []
    for la in np.arange(lat_min + dlat / 2.0, lat_max, dlat):
        for lo in np.arange(lon_min + dlon / 2.0, lon_max, dlon):
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


def _day_covered(day: date, cache_dir: Path) -> bool:
    product_id = glorys_product_for_date(day)
    for nc in cache_dir.glob("*.nc"):
        if "uo_vo" in nc.name:
            continue
        end = date.fromisoformat(nc.stem.rsplit("_", 1)[-1])
        start = date.fromisoformat(nc.stem.rsplit("_", 2)[-2])
        dataset_id = nc.name.rsplit("_", 2)[0]
        if dataset_id == product_id and start <= day <= end:
            return True
    return False


def _ensure_glorys_cov_cache(days: list[date], cache_dir: Path) -> None:
    from fishai.ingestion.physics.cufes_training_covariates import _subset_batch_live
    from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config

    missing = [d for d in days if not _day_covered(d, cache_dir)]
    if not missing:
        return
    cfg = load_overlap_config()
    log_path = REPO / str(cfg["pull_logs"]["glorys"])
    batches = plan_glorys_subset_batches(missing)
    for batch in batches:
        _subset_batch_live(batch, cache_dir, log_path=log_path)


def _batches_from_cache(days: list[date], cache_dir: Path) -> list[GlorysSubsetBatch]:
    nc_files = sorted(cache_dir.glob("*.nc"))
    by_key: dict[tuple[str, date, date], Path] = {}
    for nc in nc_files:
        end = date.fromisoformat(nc.stem.rsplit("_", 1)[-1])
        start = date.fromisoformat(nc.stem.rsplit("_", 2)[-2])
        dataset_id = nc.name.rsplit("_", 2)[0]
        by_key[(dataset_id, start, end)] = nc
    batches: list[GlorysSubsetBatch] = []
    seen: set[tuple[str, date, date]] = set()
    for day in days:
        product_id = glorys_product_for_date(day)
        hit = None
        for (dataset_id, start, end), _ in by_key.items():
            if dataset_id == product_id and start <= day <= end:
                hit = (dataset_id, start, end)
                break
        if hit is None:
            raise FileNotFoundError(f"no GLORYS cache for {day.isoformat()}")
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


def _load_store(days: list[date]) -> GlorysFieldStore:
    cfg = load_overlap_config()
    store = new_glorys_field_store_for_live_build(cfg)
    batches = _batches_from_cache(days, GLORYS_ADULT_CACHE)
    populate_store_days_from_cache(store, days, batches, GLORYS_ADULT_CACHE)
    return store


def _grid_covariates_for_day(grid: pd.DataFrame, day: date, store: GlorysFieldStore, time_idx: int) -> pd.DataFrame:
    ts = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
    sampler = store.field_sampler
    rows: list[dict[str, object]] = []
    for _, row in grid.iterrows():
        sampled = sampler(float(row["latitude"]), float(row["longitude"]), pd.Timestamp(ts))
        depth, _ = store.sample_bottom_depth_with_reason(float(row["latitude"]), float(row["longitude"]))
        rec = dict(row)
        for field in CUFES_COVARIATE_FIELDS:
            rec[field] = sampled.get(field, np.nan)
        rec["bottom_depth_m"] = depth
        rec["log_depth"] = float(np.log(depth)) if depth and depth > 0 else np.nan
        rec["time_idx"] = time_idx
        rows.append(rec)
    out = pd.DataFrame(rows)
    rename = {
        "T3m": "temp_3m_z",
        "S3m": "sal_3m_z",
        "MLD_m": "mld_z",
        "sst_grad": "sst_grad_z",
        "front_distance_km": "dist_front_z",
        "log_depth": "log_depth_z",
    }
    for src, dst in rename.items():
        if src in out.columns:
            out[dst] = out[src]
    return out


def _time_idx_for_day(day: date, origin: date, levels: list[int]) -> int:
    raw = (day - origin).days
    if raw in levels:
        return raw
    prior = [lv for lv in levels if lv <= raw]
    return max(prior) if prior else min(levels)


def _fetch_currents_batch(batch: GlorysSubsetBatch) -> Path:
    import copernicusmarine  # type: ignore[import-not-found]

    CURRENT_CACHE.mkdir(parents=True, exist_ok=True)
    out = CURRENT_CACHE / f"{batch.dataset_id}_{batch.date_start}_{batch.date_end}_uo_vo.nc"
    if out.is_file():
        return out
    lat_min, lat_max, lon_min, lon_max = batch.bbox
    copernicusmarine.subset(
        dataset_id=batch.dataset_id,
        variables=["uo", "vo"],
        minimum_depth=0.0,
        maximum_depth=5.0,
        start_datetime=batch.date_start.isoformat(),
        end_datetime=batch.date_end.isoformat(),
        minimum_latitude=lat_min,
        maximum_latitude=lat_max,
        minimum_longitude=lon_min,
        maximum_longitude=lon_max,
        output_filename=out.name,
        output_directory=str(CURRENT_CACHE),
    )
    return out


def _currents_on_grid(nc_path: Path, day: date, grid: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    ds = xr.open_dataset(nc_path)
    try:
        return _currents_on_grid_ds(ds, day, grid)
    finally:
        ds.close()


def _currents_on_grid_ds(ds: xr.Dataset, day: date, grid: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    lat_name = "latitude" if "latitude" in ds.coords else "lat"
    lon_name = "longitude" if "longitude" in ds.coords else "lon"
    time_name = "time" if "time" in ds.coords else "time_counter"
    depth_name = "depth" if "depth" in ds.coords else "deptho"
    tsel = ds.sel({time_name: np.datetime64(day)}, method="nearest")
    u = tsel["uo"]
    v = tsel["vo"]
    if depth_name in u.dims:
        u = u.isel({depth_name: 0})
        v = v.isel({depth_name: 0})
    lon_axis = np.asarray(u[lon_name].values, dtype=float)
    use360 = float(np.nanmax(lon_axis)) > 180.0
    lats = grid["latitude"].to_numpy(dtype=float)
    lons = grid["longitude"].to_numpy(dtype=float)
    if use360:
        lons = np.where(lons < 0, lons + 360.0, lons)
    u_vals = np.asarray(u.interp({lat_name: lats, lon_name: lons}, method="nearest").values, dtype=float).reshape(-1)
    v_vals = np.asarray(v.interp({lat_name: lats, lon_name: lons}, method="nearest").values, dtype=float).reshape(-1)
    return u_vals, v_vals


def _to_advection_grid(s_df: pd.DataFrame, u: np.ndarray, v: np.ndarray, template: pd.DataFrame) -> AdvectionGrid:
    merged = template.merge(s_df[["cell_id", "S"]], on="cell_id")
    xs = np.sort(merged["X"].unique())
    ys = np.sort(merged["Y"].unique())
    ny, nx = len(ys), len(xs)
    s_grid = np.zeros((ny, nx))
    u_grid = np.zeros((ny, nx))
    v_grid = np.zeros((ny, nx))
    idx_by_cell = {cid: i for i, cid in enumerate(template["cell_id"])}
    for _, row in merged.iterrows():
        ix = int(np.where(xs == row["X"])[0][0])
        iy = int(np.where(ys == row["Y"])[0][0])
        s_grid[iy, ix] = float(row["S"])
        j = idx_by_cell[row["cell_id"]]
        u_grid[iy, ix] = u[j]
        v_grid[iy, ix] = v[j]
    return AdvectionGrid(x_km=xs, y_km=ys, s=s_grid, u_ms=u_grid, v_ms=v_grid)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-fold", type=int, default=4)
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="Skip downloads/R export; score from cached grid_s and currents",
    )
    args = parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    grid = build_grid_centers()
    cov_dir = OUT_DIR / "grid_covariates"
    s_dir = OUT_DIR / "grid_s"
    cov_dir.mkdir(parents=True, exist_ok=True)
    s_dir.mkdir(parents=True, exist_ok=True)

    # Pass 1: R export events + OOF only (needs events file for source days)
    events_path = OUT_DIR / "hindcast_events.csv"
    if not args.score_only and not events_path.is_file():
        subprocess.run(
            [
                "Rscript",
                str(REPO / "scripts/models/run_jack_mackerel_advection_hindcast.R"),
                "--test-fold",
                str(args.test_fold),
            ],
            cwd=str(REPO),
            check=True,
        )
    events = pd.read_csv(events_path)
    origin = date(1990, 1, 1)
    time_levels = sorted(
        {
            (pd.Timestamp(t, tz="UTC").date() - origin).days
            for t in events["time"]
        }
    )
    source_days = sorted(events["source_day"].astype(str).unique())
    days = [date.fromisoformat(d) for d in source_days]

    if not args.score_only:
        _ensure_glorys_cov_cache(days, GLORYS_ADULT_CACHE)
        store = _load_store(days)
    for day in days:
        if args.score_only:
            break
        cov_path = cov_dir / f"{day.isoformat()}.csv"
        if cov_path.is_file():
            continue
        tidx = _time_idx_for_day(day, origin, time_levels)
        cov = _grid_covariates_for_day(grid, day, store, tidx)
        cov.to_csv(cov_path, index=False)

    current_map: dict[date, Path] = {}
    if args.score_only:
        for nc in sorted(CURRENT_CACHE.glob("*_uo_vo.nc")):
            core = nc.stem.removesuffix("_uo_vo")
            end = date.fromisoformat(core.rsplit("_", 1)[-1])
            start = date.fromisoformat(core.rsplit("_", 2)[-2])
            d = start
            while d <= end:
                if d in days:
                    current_map[d] = nc
                d += __import__("datetime").timedelta(days=1)
    for batch in ([] if args.score_only else plan_glorys_subset_batches(days)):
        nc = _fetch_currents_batch(
            GlorysSubsetBatch(
                dataset_id=batch.dataset_id,
                date_start=batch.date_start,
                date_end=batch.date_end,
                variables=("uo", "vo"),
                bbox=PILOT_BBOX,
            )
        )
        d = batch.date_start
        while d <= batch.date_end:
            if d in days:
                current_map[d] = nc
            d += __import__("datetime").timedelta(days=1)

    if not args.score_only:
        subprocess.run(
            [
                "Rscript",
                str(REPO / "scripts/models/run_jack_mackerel_advection_hindcast.R"),
                "--test-fold",
                str(args.test_fold),
                "--grids-only",
            ],
            cwd=str(REPO),
            check=True,
        )

    grid_cache: dict[str, AdvectionGrid] = {}
    nc_day_lists: dict[Path, list[str]] = {}
    for day_str in source_days:
        d = date.fromisoformat(day_str)
        nc = current_map.get(d)
        if nc is not None and (s_dir / f"{day_str}.csv").is_file():
            nc_day_lists.setdefault(nc, []).append(day_str)

    def get_grid(day_str: str) -> AdvectionGrid | None:
        if day_str in grid_cache:
            return grid_cache[day_str]
        s_path = s_dir / f"{day_str}.csv"
        if not s_path.is_file():
            return None
        d = date.fromisoformat(day_str)
        nc = current_map.get(d)
        if nc is None:
            return None
        s_df = pd.read_csv(s_path)
        u, v = _currents_on_grid(nc, d, grid)
        g = _to_advection_grid(s_df, u, v, grid)
        grid_cache[day_str] = g
        return g

    train = events[events["fold_id"] != args.test_fold]
    test = events[events["fold_id"] == args.test_fold]

    field_cache: dict[tuple[str, float, float], np.ndarray] = {}

    def adv_prob(row: pd.Series, sigma: float, alpha: float) -> float:
        day = str(row["source_day"])
        g = get_grid(day)
        if g is None:
            return float("nan")
        key = (day, sigma, alpha)
        if key not in field_cache:
            from fishai.evaluation.advection_sdm import advection_taxis_field

            field_cache[key] = advection_taxis_field(g, sigma_km=sigma, alpha=alpha)
        field = field_cache[key]
        from fishai.evaluation.advection_sdm import _bilinear_at

        return _bilinear_at(float(row["X"]), float(row["Y"]), g, field)

    def predict(row: pd.Series, sigma: float, alpha: float, lane: str) -> float:
        g = get_grid(str(row["source_day"]))
        if g is None:
            return float("nan")
        if lane == "persistence":
            return persistence_at_point(g, float(row["X"]), float(row["Y"]))
        return adv_prob(row, sigma, alpha)

    def brier_adv_cached(sigma: float, alpha: float, frame: pd.DataFrame) -> float:
        ys, ps = [], []
        for _, row in frame.iterrows():
            p = adv_prob(row, sigma, alpha)
            if math.isnan(p):
                continue
            ys.append(int(row["z"]))
            ps.append(p)
        return brier_score(ys, ps) if len(ps) >= 5 else 1.0

    opt = brute(
        lambda x: brier_adv_cached(x[0], x[1], train),
        (slice(15.0, 45.0, 15.0), slice(0.0, 1.0, 1.0)),
        finish=None,
    )
    sigma_hat, alpha_hat = float(opt[0]), float(opt[1])

    def score_frame(frame: pd.DataFrame) -> dict[str, float | int]:
        rows: list[dict[str, float | int]] = []
        for _, row in frame.iterrows():
            p_adv = predict(row, sigma_hat, alpha_hat, "advection")
            p_persist = predict(row, sigma_hat, alpha_hat, "persistence")
            p_sdm = float(row["p_sdm"])
            if not all(math.isfinite(x) for x in (p_adv, p_persist, p_sdm)):
                continue
            rows.append(
                {
                    "z": int(row["z"]),
                    "sdm_alone": p_sdm,
                    "advection_taxis": float(p_adv),
                    "persistence": float(p_persist),
                }
            )
        if len(rows) < 5:
            return {"n_events": len(rows), "brier_sdm_alone": float("nan"), "auc_sdm_alone": float("nan")}
        ys = [r["z"] for r in rows]
        out: dict[str, float | int] = {"n_events": len(rows)}
        for name in ("sdm_alone", "advection_taxis", "persistence"):
            clipped = [min(max(float(r[name]), 0.0), 1.0) for r in rows]
            out[f"brier_{name}"] = brier_score(ys, clipped)
            out[f"auc_{name}"] = (
                float(roc_auc_score(ys, clipped)) if len(set(ys)) > 1 else float("nan")
            )
        return out

    report = {
        "species": "Pacific jack mackerel (all sizes)",
        "model_config": "configs/models/jack_mackerel_encounter_all_sizes.yaml",
        "test_fold": args.test_fold,
        "fitted_parameters": {"sigma_km": sigma_hat, "alpha": alpha_hat},
        "n_hindcast_events_total": int(len(events)),
        "n_grid_days_with_currents": len(grid_cache),
        "train_subset": score_frame(train),
        "test_subset": score_frame(test),
        "all_events": score_frame(events),
    }
    report["advection_beats_sdm_on_test_brier"] = (
        report["test_subset"]["brier_advection_taxis"] < report["test_subset"]["brier_sdm_alone"]
    )
    out_path = OUT_DIR / "advection_hindcast_scores.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
