#!/usr/bin/env python3
"""Export 24h issued-WCOFS encounter probability grids for PDS cutoffs (SCB GLORYS grid)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

# Reuse sampler helpers
import importlib.util

_sampler_path = REPO_ROOT / "scripts/models/sample_jack_mackerel_24h_wcofs_covariates.py"
_spec = importlib.util.spec_from_file_location("sample_jack_mackerel_24h_wcofs_covariates", _sampler_path)
sampler = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(sampler)


def _grid_covariate_table(fields: dict, lat_dst: np.ndarray, lon_dst: np.ndarray, depth_m: np.ndarray) -> pd.DataFrame:
    nj, ni = len(lat_dst), len(lon_dst)
    rows: list[dict] = []
    for j in range(nj):
        for i in range(ni):
            d = float(depth_m[j, i])
            if not np.isfinite(d) or d <= 0:
                continue
            row = {"lat": float(lat_dst[j]), "lon": float(lon_dst[i]), "log_depth_m": float(np.log(d))}
            ok = True
            for raw in ("T3m", "S3m", "MLD_m", "sst_grad", "front_distance_km"):
                val = float(fields[raw][j, i])
                if not np.isfinite(val):
                    ok = False
                    break
                row[raw] = val
            if ok:
                rows.append(row)
    return pd.DataFrame(rows)


def main(argv: list[str] | None = None) -> int:
    from fishai.ingestion.physics.wcofs_glorys_overlap import glorys_grid_from_config, load_overlap_config
    from fishai.ingestion.physics.wcofs_pds_s3_list import list_keys_under_prefix
    from fishai.ingestion.sources import load_sources_manifest

    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--cutoff", required=True, help="ISO cutoff date with PDS f024")
    parser.add_argument("--checkpoint-rds", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args(argv)

    inv = json.loads(args.inventory.read_text(encoding="utf-8"))
    cutoff = dt.date.fromisoformat(args.cutoff)
    if cutoff.isoformat() not in (inv.get("cutoffs_with_f024") or []):
        raise SystemExit(f"cutoff {cutoff} not in PDS f024 inventory")

    manifest = load_sources_manifest()
    pilot = manifest.get("pilot") or {}
    box = pilot.get("bbox") or {}
    bbox = (float(box["lat_min"]), float(box["lat_max"]), float(box["lon_min"]), float(box["lon_max"]))
    config = load_overlap_config()
    lat_dst, lon_dst = glorys_grid_from_config(config)

    # Static depth z from training-table builder path (GLORYS/WCOFS bathymetry on grid)
    from fishai.ingestion.physics.wcofs_h_glorys_store import load_wcofs_h_glorys_grid

    h_grid = load_wcofs_h_glorys_grid(verify_sha256=False)
    depth_m = np.asarray(h_grid.h_m, dtype=float)

    ds, key, err = sampler._fetch_wcofs_fields(cutoff, "f024", bbox)
    if ds is None:
        raise SystemExit(err or "missing f024")
    try:
        fields = sampler._prepared_fields_from_ds(ds, config)
        if fields is None:
            raise SystemExit("unsupported_wcofs_product")
        grid = _grid_covariate_table(fields, lat_dst, lon_dst, depth_m)
    finally:
        ds.close()

    train_path = REPO_ROOT / "data/processed/adult_cps/adult_cps_training_table.parquet"
    train = pd.read_parquet(train_path)
    train = train[train["species"] == "Trachurus symmetricus"]
    z_map = {
        "temp_3m_z": "T3m",
        "sal_3m_z": "S3m",
        "mld_z": "MLD_m",
        "sst_grad_z": "sst_grad",
        "dist_front_z": "front_distance_km",
        "log_depth_z": "bottom_depth_m",
    }
    for z_col, raw in z_map.items():
        if raw == "bottom_depth_m":
            ref = np.log(train["bottom_depth_m"].astype(float))
            mu = float(ref.mean())
            sd = float(ref.std(ddof=0))
            if not np.isfinite(sd) or sd <= 0:
                sd = 1.0
            grid[z_col] = (grid["log_depth_m"] - mu) / sd
            continue
        if raw not in train.columns:
            raise SystemExit(f"training table missing upstream column {raw} for {z_col}")
        mu = float(train[raw].mean())
        sd = float(train[raw].std(ddof=0))
        if not np.isfinite(sd) or sd <= 0:
            sd = 1.0
        grid[z_col] = (grid[raw] - mu) / sd

    grid_path = args.output_csv.with_suffix(".grid_covariates.parquet")
    grid_path.parent.mkdir(parents=True, exist_ok=True)
    grid.to_parquet(grid_path, index=False)

    r_script = REPO_ROOT / "scripts" / "models" / "predict_jack_mackerel_grid_from_checkpoint.R"
    cmd = [
        "Rscript",
        str(r_script),
        "--checkpoint",
        str(args.checkpoint_rds),
        "--grid-parquet",
        str(grid_path),
        "--cutoff",
        cutoff.isoformat(),
        "--output",
        str(args.output_csv),
        "--wcofs-key",
        key or "",
    ]
    subprocess.check_call(cmd, cwd=str(REPO_ROOT), env={**dict(**os.environ), "FISHAI_ROOT": str(REPO_ROOT)})
    return 0


if __name__ == "__main__":
    import os

    raise SystemExit(main())
