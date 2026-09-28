"""Load WCOFS cycle files from processed storage for validation commands."""

from __future__ import annotations

from pathlib import Path

import xarray as xr

from fishai.ingestion.sensors.internal.config import REPO_ROOT, load_sensors_config


def load_wcofs_cycle(cycle_yyyymmdd: str) -> xr.Dataset:
    cfg = load_sensors_config()
    pattern = cfg["paths"]["wcofs_cycle_glob"].replace("{cycle}", cycle_yyyymmdd)
    root = REPO_ROOT
    matches = sorted(root.glob(pattern))
    if not matches:
        raise FileNotFoundError(
            f"No WCOFS file for cycle {cycle_yyyymmdd}; expected under {pattern}"
        )
    return xr.open_dataset(matches[-1]).load()
