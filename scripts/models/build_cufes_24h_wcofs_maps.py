#!/usr/bin/env python3
"""Example 24 h-ahead WCOFS-forced covariate / encounter pipeline maps on the 10 km grid."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
from fishai.ingestion.sensors.internal.grid import build_training_grid_10km
from fishai.models.cufes_24h_wcofs_forcing import (
    open_wcofs_24h_forecast_fields,
    wcofs_covariates_on_target_grid,
)


def _plot_field(
    lats: np.ndarray,
    lons: np.ndarray,
    field: np.ndarray,
    *,
    title: str,
    out_path: Path,
    cbar_label: str,
) -> None:
    lon2d, lat2d = np.meshgrid(lons, lats)
    fig, ax = plt.subplots(figsize=(8, 6), dpi=120)
    pcm = ax.pcolormesh(lon2d, lat2d, field, shading="auto", cmap="viridis")
    fig.colorbar(pcm, ax=ax, label=cbar_label)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(title)
    ax.set_aspect("equal")
    fig.text(
        0.5,
        0.01,
        "Pipeline demo — egg-encounter model not scored on this grid until validation passes.",
        ha="center",
        fontsize=8,
        color="dimgray",
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cycle-date",
        type=str,
        default=None,
        help="WCOFS 03Z cycle date (UTC). Default: latest reachable recent cycle.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPO / "artifacts/cufes_24h_wcofs_prediction/maps",
    )
    args = parser.parse_args()

    cfg = load_overlap_config()
    bbox = cfg["pilot_bbox"]
    pilot_cfg = {"bbox": bbox, "training_grid": {"spacing_km": 10.0}}
    grid = build_training_grid_10km(pilot_cfg)
    lat_dst = grid["lat"].values
    lon_dst = grid["lon"].values
    bbox_tuple = (
        float(bbox["lat_min"]),
        float(bbox["lat_max"]),
        float(bbox["lon_min"]),
        float(bbox["lon_max"]),
    )

    if args.cycle_date:
        cycle = dt.date.fromisoformat(args.cycle_date)
    else:
        cycle = dt.date(2024, 9, 5)

    ds = open_wcofs_24h_forecast_fields(cycle, bbox=bbox_tuple)
    cov, meta = wcofs_covariates_on_target_grid(ds, lat_dst=lat_dst, lon_dst=lon_dst, config=cfg)

    t3m = cov["T3m"].values
    meta_out = {
        "cycle_date": cycle.isoformat(),
        "lead_tag": "f024",
        "forcing_source": "wcofs_forecast",
        "grid_spacing_km": 10.0,
        "product": "egg_encounter_pipeline_demo",
        **meta,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "map_metadata.json").write_text(json.dumps(meta_out, indent=2), encoding="utf-8")

    _plot_field(
        lat_dst,
        lon_dst,
        t3m,
        title=f"WCOFS 24 h T3m (egg-forcing demo) — cycle {cycle.isoformat()}",
        out_path=args.out_dir / "wcofs_24h_t3m_10km.png",
        cbar_label="Temperature at 3 m (°C)",
    )
    print(json.dumps(meta_out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
