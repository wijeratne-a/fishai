"""Persist sensor pulls under gitignored data trees."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import xarray as xr

from fishai.ingestion.sensors.internal.config import REPO_ROOT, load_sensors_config


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _prepare_tabular_archive(df: pd.DataFrame) -> pd.DataFrame:
    """Public instrument positions as plain float lat/lon (no GeoJSON/geometry columns)."""
    out = df.copy()
    forbidden = [c for c in out.columns if str(c).lower() in {"geometry", "wkt", "geojson"}]
    if forbidden:
        out = out.drop(columns=forbidden)
    if "latitude" in out.columns and "lat" not in out.columns:
        out["lat"] = pd.to_numeric(out["latitude"], errors="coerce")
    if "longitude" in out.columns and "lon" not in out.columns:
        out["lon"] = pd.to_numeric(out["longitude"], errors="coerce")
    drop_cols = [c for c in ("latitude", "longitude") if c in out.columns]
    if drop_cols:
        out = out.drop(columns=drop_cols)
    return out


def _assert_processed_path(path: Path) -> None:
    rel = path.relative_to(REPO_ROOT).as_posix()
    if not rel.startswith("data/processed/"):
        raise ValueError(f"sensor archive must live under data/processed/, got {rel}")


def append_hfr_zarr(ds: xr.Dataset, cfg: dict[str, Any] | None = None) -> Path:
    cfg = cfg or load_sensors_config()
    rel = cfg["paths"]["hfr_zarr"]
    zpath = REPO_ROOT / rel
    _ensure_parent(zpath)
    chunked = ds.chunk({"time": 24, "latitude": 64, "longitude": 64})
    _assert_processed_path(zpath)
    if zpath.exists():
        existing = xr.open_zarr(zpath)
        combined = xr.concat([existing, chunked], dim="time")
        combined = combined.drop_duplicates("time", keep="last")
        combined.to_zarr(zpath, mode="w")
    else:
        chunked.to_zarr(zpath, mode="w")
    return zpath


def write_ndbc_parquet(df: pd.DataFrame, day: datetime, cfg: dict[str, Any] | None = None) -> Path | None:
    if df.empty:
        return None
    cfg = cfg or load_sensors_config()
    root = REPO_ROOT / cfg["paths"]["ndbc_parquet_root"]
    if day.tzinfo is None:
        day = day.replace(tzinfo=timezone.utc)
    else:
        day = day.astimezone(timezone.utc)
    part = root / f"date={day:%Y-%m-%d}" / "observations.parquet"
    _ensure_parent(part)
    _assert_processed_path(part)
    _prepare_tabular_archive(df).to_parquet(part, index=False)
    return part


def write_glider_parquet(
    df: pd.DataFrame,
    dataset_id: str,
    day: datetime,
    cfg: dict[str, Any] | None = None,
) -> Path | None:
    if df.empty:
        return None
    cfg = cfg or load_sensors_config()
    root = REPO_ROOT / cfg["paths"]["gliders_parquet_root"]
    if day.tzinfo is None:
        day = day.replace(tzinfo=timezone.utc)
    else:
        day = day.astimezone(timezone.utc)
    safe_id = dataset_id.replace("/", "_")
    part = root / f"date={day:%Y-%m-%d}" / f"{safe_id}.parquet"
    _ensure_parent(part)
    _assert_processed_path(part)
    _prepare_tabular_archive(df).to_parquet(part, index=False)
    return part
