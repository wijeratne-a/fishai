"""WCOFS ``h`` GLORYS-grid artifact manifest and loader."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from fishai.ingestion.physics.wcofs_h_glorys_store import (
    MODEL_FLOOR_TOLERANCE_M,
    build_wcofs_h_glorys_grid,
    depth_at_model_floor,
    export_wcofs_h_glorys_grid,
    load_wcofs_h_glorys_grid,
    load_wcofs_h_manifest,
    resolve_roms_hmin_m,
    write_wcofs_h_manifest,
)


def _mini_wcofs(h_value: float = 120.0, hmin_attr: float | None = None) -> xr.Dataset:
    n = 5
    lat = np.linspace(33.0, 33.4, n)
    lon = np.linspace(-120.4, -120.0, n)
    lat2d = np.broadcast_to(lat[:, None], (n, n))
    lon2d = np.broadcast_to(lon[None, :], (n, n))
    attrs: dict = {}
    if hmin_attr is not None:
        attrs["hmin"] = hmin_attr
    return xr.Dataset(
        {
            "h": (("eta_rho", "xi_rho"), np.full((n, n), h_value)),
            "mask_rho": (("eta_rho", "xi_rho"), np.ones((n, n))),
            "lat_rho": (("eta_rho", "xi_rho"), lat2d),
            "lon_rho": (("eta_rho", "xi_rho"), lon2d),
            "zeta": (("eta_rho", "xi_rho"), np.zeros((n, n))),
        },
        attrs=attrs,
    )


def test_resolve_roms_hmin_from_netcdf_global_attr() -> None:
    ds = _mini_wcofs(h_value=80.0, hmin_attr=5.0)
    val, source = resolve_roms_hmin_m(ds)
    assert val == 5.0
    assert source == "netcdf_global_attr_hmin"


def test_resolve_roms_hmin_from_wet_cell_minimum() -> None:
    ds = _mini_wcofs(h_value=42.0)
    val, source = resolve_roms_hmin_m(ds)
    assert val == 42.0
    assert source == "wet_cell_minimum_h"


def test_manifest_round_trip_and_loader(tmp_path: Path) -> None:
    ds = _mini_wcofs()
    artifact = tmp_path / "h.zarr"
    manifest = tmp_path / "manifest.json"
    export_wcofs_h_glorys_grid(
        ds,
        source_file="s3://test/wcofs.nc",
        artifact_path=artifact,
        manifest_path=manifest,
    )
    doc = load_wcofs_h_manifest(manifest)
    assert doc["source_variable"] == "h"
    assert doc["regridding_rule"] == "area_weighted_wet_masked"
    assert doc["sha256"]
    assert doc["roms_hmin_m"] == doc["roms_hmin_m"]
    loaded = load_wcofs_h_glorys_grid(manifest_path=manifest, artifact_path=artifact)
    assert loaded.h_m.shape == loaded.has_source.shape
    assert np.isfinite(loaded.h_m).any()


def test_loader_rejects_sha_mismatch(tmp_path: Path) -> None:
    ds = _mini_wcofs()
    artifact = tmp_path / "h.zarr"
    manifest = tmp_path / "manifest.json"
    export_wcofs_h_glorys_grid(ds, artifact_path=artifact, manifest_path=manifest)
    bad = json.loads(manifest.read_text(encoding="utf-8"))
    bad["sha256"] = "0" * 64
    write_wcofs_h_manifest(bad, manifest_path=manifest)
    with pytest.raises(ValueError, match="sha256"):
        load_wcofs_h_glorys_grid(manifest_path=manifest, artifact_path=artifact)


def test_depth_at_model_floor_within_tolerance() -> None:
    hmin = 10.0
    assert depth_at_model_floor(10.4, hmin, tolerance_m=MODEL_FLOOR_TOLERANCE_M)
    assert not depth_at_model_floor(11.0, hmin, tolerance_m=MODEL_FLOOR_TOLERANCE_M)
    assert not depth_at_model_floor(float("nan"), hmin)
