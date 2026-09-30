"""Regridded WCOFS ROMS ``h`` on the GLORYS 1/12° pilot grid (artifact + manifest)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr

from fishai.ingestion.physics.bathymetry import (
    WCOFS_BOTTOM_DEPTH_SOURCE,
    WCOFS_BOTTOM_DEPTH_VARIABLE,
)
from fishai.ingestion.physics.wcofs_glorys_grid import coarsen_wcofs_h_to_glorys
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    coarsen_min_wet_fraction,
    glorys_grid_from_config,
    load_overlap_config,
)
from fishai.ingestion.sources import REPO_ROOT

MANIFEST_SCHEMA_VERSION = 1
DEFAULT_ARTIFACT_REL = "data/derived/physics/wcofs_h_glorys_pilot.zarr"
DEFAULT_MANIFEST_REL = "data/derived/manifests/wcofs_h_glorys_grid.json"
MODEL_FLOOR_TOLERANCE_M = 0.5

HMIN_ATTR_KEYS = ("hmin", "Hmin", "minimum_depth", "Minimum_Depth")
HMIN_VAR_NAMES = ("hmin", "Hmin", "minimum_depth")


@dataclass(frozen=True)
class WcofsHGlorysGrid:
    """Static WCOFS bathymetry on the GLORYS-class grid (training + prediction parity)."""

    lat: np.ndarray
    lon: np.ndarray
    h_m: np.ndarray
    has_source: np.ndarray
    wet_fraction: np.ndarray
    min_wet_fraction: float
    roms_hmin_m: float
    hmin_source: str
    regridding_rule: str
    source_variable: str
    source_file: str


def _surface_slab(ds: xr.Dataset) -> xr.Dataset:
    if "lead_hours" in ds.dims:
        ds = ds.isel(lead_hours=0)
    return ds.isel(ocean_time=0) if "ocean_time" in ds.dims else ds


def resolve_roms_hmin_m(ds: xr.Dataset) -> tuple[float, str]:
    """
    ROMS minimum depth (m, positive down).

    Prefer global NetCDF attributes or ``hmin`` variables; otherwise the minimum
    of ``h`` over wet rho cells (never a hardcoded guess).
    """
    for key in HMIN_ATTR_KEYS:
        if key in ds.attrs:
            val = float(ds.attrs[key])
            if np.isfinite(val) and val > 0:
                return val, f"netcdf_global_attr_{key}"
    slab = _surface_slab(ds)
    for name in HMIN_VAR_NAMES:
        if name in slab:
            val = float(np.asarray(slab[name].values).ravel()[0])
            if np.isfinite(val) and val > 0:
                return val, f"netcdf_variable_{name}"
        if name in ds:
            val = float(np.asarray(ds[name].values).ravel()[0])
            if np.isfinite(val) and val > 0:
                return val, f"netcdf_variable_{name}"
    wet = np.asarray(slab.mask_rho.values == 1, dtype=bool)
    h = np.asarray(slab.h.values, dtype=float)
    wet_h = h[wet & np.isfinite(h) & (h > 0)]
    if wet_h.size == 0:
        raise ValueError("wcofs: cannot resolve ROMS hmin (no wet h cells)")
    return float(np.min(wet_h)), "wet_cell_minimum_h"


def build_wcofs_h_glorys_grid(
    ds_wcofs: xr.Dataset,
    *,
    config: dict[str, Any] | None = None,
    source_file: str = "",
) -> WcofsHGlorysGrid:
    cfg = config or load_overlap_config()
    lat_dst, lon_dst = glorys_grid_from_config(cfg)
    min_wet = coarsen_min_wet_fraction(cfg)
    h_m, has_source, wet_fraction = coarsen_wcofs_h_to_glorys(
        ds_wcofs,
        lat_dst,
        lon_dst,
        min_wet_fraction=min_wet,
    )
    hmin_m, hmin_source = resolve_roms_hmin_m(ds_wcofs)
    bathy = cfg.get("bathymetry") or {}
    return WcofsHGlorysGrid(
        lat=np.asarray(lat_dst, dtype=float),
        lon=np.asarray(lon_dst, dtype=float),
        h_m=h_m,
        has_source=has_source,
        wet_fraction=wet_fraction,
        min_wet_fraction=min_wet,
        roms_hmin_m=hmin_m,
        hmin_source=hmin_source,
        regridding_rule=str(bathy.get("coarsen", "area_weighted_wet_masked")),
        source_variable=WCOFS_BOTTOM_DEPTH_VARIABLE,
        source_file=source_file or str(ds_wcofs.attrs.get("wcofs_s3_key", "")),
    )


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_dir():
        for child in sorted(path.rglob("*")):
            if child.is_file():
                rel = child.relative_to(path).as_posix().encode()
                digest.update(rel)
                digest.update(child.read_bytes())
    else:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def write_wcofs_h_glorys_artifact(
    grid: WcofsHGlorysGrid,
    artifact_path: Path | None = None,
) -> Path:
    artifact_path = Path(artifact_path or (REPO_ROOT / DEFAULT_ARTIFACT_REL))
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    ds = xr.Dataset(
        {
            "h": (("lat", "lon"), grid.h_m),
            "has_source": (("lat", "lon"), grid.has_source.astype(np.uint8)),
            "wet_fraction": (("lat", "lon"), grid.wet_fraction),
        },
        coords={"lat": grid.lat, "lon": grid.lon},
        attrs={
            "source": WCOFS_BOTTOM_DEPTH_SOURCE,
            "source_variable": grid.source_variable,
            "source_file": grid.source_file,
            "regridding_rule": grid.regridding_rule,
            "min_wet_fraction": grid.min_wet_fraction,
            "roms_hmin_m": grid.roms_hmin_m,
            "hmin_source": grid.hmin_source,
            "grid": "glorys_1_12deg",
        },
    )
    ds.to_zarr(artifact_path, mode="w", consolidated=True)
    return artifact_path


def manifest_record_from_grid(
    grid: WcofsHGlorysGrid,
    *,
    artifact_path: Path,
    sha256: str,
) -> dict[str, Any]:
    try:
        artifact_rel = artifact_path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        artifact_rel = artifact_path.as_posix()
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "artifact_path": artifact_rel,
        "sha256": sha256,
        "source_file": grid.source_file,
        "source_variable": grid.source_variable,
        "source": WCOFS_BOTTOM_DEPTH_SOURCE,
        "regridding_rule": grid.regridding_rule,
        "min_wet_fraction": grid.min_wet_fraction,
        "roms_hmin_m": grid.roms_hmin_m,
        "hmin_source": grid.hmin_source,
        "model_floor_tolerance_m": MODEL_FLOOR_TOLERANCE_M,
    }


def write_wcofs_h_manifest(
    record: dict[str, Any],
    manifest_path: Path | None = None,
) -> Path:
    manifest_path = Path(manifest_path or (REPO_ROOT / DEFAULT_MANIFEST_REL))
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


def export_wcofs_h_glorys_grid(
    ds_wcofs: xr.Dataset,
    *,
    config: dict[str, Any] | None = None,
    source_file: str = "",
    artifact_path: Path | None = None,
    manifest_path: Path | None = None,
) -> tuple[Path, Path, WcofsHGlorysGrid]:
    """Build grid, write Zarr artifact (uncommitted data), update committed manifest."""
    grid = build_wcofs_h_glorys_grid(ds_wcofs, config=config, source_file=source_file)
    artifact = write_wcofs_h_glorys_artifact(grid, artifact_path=artifact_path)
    sha = _sha256_path(artifact)
    record = manifest_record_from_grid(grid, artifact_path=artifact, sha256=sha)
    manifest = write_wcofs_h_manifest(record, manifest_path=manifest_path)
    return artifact, manifest, grid


def load_wcofs_h_manifest(manifest_path: Path | None = None) -> dict[str, Any]:
    path = Path(manifest_path or (REPO_ROOT / DEFAULT_MANIFEST_REL))
    return json.loads(path.read_text(encoding="utf-8"))


def load_wcofs_h_glorys_grid(
    *,
    manifest_path: Path | None = None,
    artifact_path: Path | None = None,
    verify_sha256: bool = True,
) -> WcofsHGlorysGrid:
    """
    Load the regridded WCOFS ``h`` grid for prediction / training (PR #5 parity).

    Raises ``FileNotFoundError`` when the artifact is missing (typical in CI).
    """
    manifest = load_wcofs_h_manifest(manifest_path)
    rel = manifest.get("artifact_path") or DEFAULT_ARTIFACT_REL
    if artifact_path is not None:
        path = Path(artifact_path)
    else:
        candidate = Path(rel)
        path = candidate if candidate.is_absolute() else REPO_ROOT / rel
    if not path.exists():
        raise FileNotFoundError(f"wcofs h glorys artifact not found: {path}")
    if verify_sha256 and manifest.get("sha256"):
        expected = str(manifest["sha256"])
        actual = _sha256_path(path)
        if actual != expected:
            raise ValueError(f"wcofs h artifact sha256 mismatch: expected {expected}, got {actual}")
    ds = xr.open_zarr(path)
    attrs = dict(ds.attrs)

    def _meta(key: str, default: Any = None) -> Any:
        val = manifest.get(key)
        if val is None:
            val = attrs.get(key, default)
        return val

    roms_hmin = _meta("roms_hmin_m")
    if roms_hmin is None:
        raise ValueError("wcofs h artifact missing roms_hmin_m in manifest and zarr attrs")
    min_wet = _meta("min_wet_fraction", 0.5)
    return WcofsHGlorysGrid(
        lat=np.asarray(ds["lat"].values, dtype=float),
        lon=np.asarray(ds["lon"].values, dtype=float),
        h_m=np.asarray(ds["h"].values, dtype=float),
        has_source=np.asarray(ds["has_source"].values, dtype=bool),
        wet_fraction=np.asarray(ds["wet_fraction"].values, dtype=float),
        min_wet_fraction=float(min_wet),
        roms_hmin_m=float(roms_hmin),
        hmin_source=str(_meta("hmin_source", "")),
        regridding_rule=str(_meta("regridding_rule", "")),
        source_variable=str(_meta("source_variable", WCOFS_BOTTOM_DEPTH_VARIABLE)),
        source_file=str(_meta("source_file", "")),
    )


def depth_at_model_floor(
    bottom_depth_m: float,
    roms_hmin_m: float,
    *,
    tolerance_m: float = MODEL_FLOOR_TOLERANCE_M,
) -> bool:
    if not np.isfinite(bottom_depth_m) or not np.isfinite(roms_hmin_m):
        return False
    return abs(bottom_depth_m - roms_hmin_m) <= float(tolerance_m)
