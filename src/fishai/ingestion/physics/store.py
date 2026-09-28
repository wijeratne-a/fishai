"""Zarr and Parquet writers for physics features (no raw vessel coordinates)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import xarray as xr
except ImportError:  # pragma: no cover
    xr = None  # type: ignore[assignment,misc]


def write_gridded_zarr(ds: Any, path: Path) -> None:
    """Write an xarray Dataset to Zarr (creates parent dirs)."""
    if xr is None:
        raise RuntimeError("xarray is required for Zarr output")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ds.to_zarr(path, mode="w", consolidated=False)


def training_parquet(
    rows: list[dict[str, Any]],
    path: Path,
) -> pd.DataFrame:
    """Parquet keyed by ``sample_id`` for training aggregates."""
    df = pd.DataFrame(rows)
    if "sample_id" not in df.columns:
        raise ValueError("training rows require sample_id")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return df


def inference_parquet(
    rows: list[dict[str, Any]],
    path: Path,
) -> pd.DataFrame:
    """Parquet keyed by ``cell_id`` and ``valid_time`` for inference."""
    df = pd.DataFrame(rows)
    for col in ("cell_id", "valid_time"):
        if col not in df.columns:
            raise ValueError(f"inference rows require {col}")
    for col in ("source", "qc_flags", "lead_hours"):
        if col not in df.columns:
            df[col] = np.nan if col == "lead_hours" else ""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return df


def cell_id_from_indices(j: int, i: int, lead_hours: int = 0) -> str:
    return f"c{j:04d}_{i:04d}_L{int(lead_hours):03d}"
