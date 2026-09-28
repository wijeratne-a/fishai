"""WCOFS×GLORYS harmonization coverage diagnostics (report-only; no training impact)."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from fishai.ingestion.physics.covariates import (
    COL_EVENT_ID,
    COL_START_LAT,
    COL_START_LON,
    COL_STOP_LAT,
    COL_STOP_LON,
    event_midpoint_lat_lon,
)
from fishai.ingestion.physics.harmonize import assign_glorys_cell_indices
from fishai.ingestion.physics.vertical import GLORYS_TOP_LEVEL_DEPTH_M, interp_at_depth_from_z_levels
from fishai.ingestion.physics.wcofs_glorys_grid import WcofsGlorysGrid, min_wet_fraction_from_config
from fishai.ingestion.sources import REPO_ROOT

DEFAULT_REPORT_JSON = (
    REPO_ROOT / "artifacts" / "harmonization" / "wcofs_glorys_overlap" / "coverage_report.json"
)
DEFAULT_REPORT_CSV = (
    REPO_ROOT / "artifacts" / "harmonization" / "wcofs_glorys_overlap" / "coverage_cells.csv"
)
DEFAULT_CUFES_FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "cufes_coverage_event_index.csv"
)


@dataclass
class CoverageLevelSpec:
    name: str
    depth_m: float


COVERAGE_LEVEL_SPECS: tuple[CoverageLevelSpec, ...] = (
    CoverageLevelSpec("surface_0m", 0.0),
    CoverageLevelSpec("sst_glorys_top_0p494m", GLORYS_TOP_LEVEL_DEPTH_M),
    CoverageLevelSpec("T3m_3m", 3.0),
    CoverageLevelSpec("S3m_3m", 3.0),
    CoverageLevelSpec("MLD_m", 3.0),
)


def _depth_grid_index(depth_grid_m: np.ndarray, depth_m: float) -> int:
    idx = int(np.argmin(np.abs(depth_grid_m - depth_m)))
    return idx


def glorys_ocean_mask_at_depth(
    z_levels: np.ndarray,
    thetao: np.ndarray,
    depth_m: float,
) -> np.ndarray:
    """GLORYS ocean (finite temperature) at ``depth_m`` on the GLORYS subgrid."""
    nj, ni = thetao.shape[-2], thetao.shape[-1]
    out = np.zeros((nj, ni), dtype=bool)
    for j in range(nj):
        for i in range(ni):
            col = thetao[:, j, i]
            if not np.isfinite(col).any():
                continue
            val = interp_at_depth_from_z_levels(
                z_levels, col, depth_m, extrapolate_above_top=True
            )
            out[j, i] = np.isfinite(val)
    return out


def wcofs_insufficient_coverage_mask(
    gridded: WcofsGlorysGrid,
    depth_m: float,
    *,
    min_wet_fraction: float,
) -> np.ndarray:
    """Cells where WCOFS coarsening blanks values due to ``wet_fraction`` gating."""
    k = _depth_grid_index(gridded.depth_m, depth_m)
    wf = gridded.wet_fraction[:, :, k]
    return np.isfinite(wf) & (wf < min_wet_fraction)


def harmonization_gap_mask(
    gridded: WcofsGlorysGrid,
    z_levels: np.ndarray,
    thetao: np.ndarray,
    depth_m: float,
    *,
    min_wet_fraction: float,
) -> np.ndarray:
    """GLORYS ocean at depth but WCOFS ``wet_fraction`` below threshold."""
    ocean = glorys_ocean_mask_at_depth(z_levels, thetao, depth_m)
    insufficient = wcofs_insufficient_coverage_mask(
        gridded, depth_m, min_wet_fraction=min_wet_fraction
    )
    return ocean & insufficient


def _count_cells(mask: np.ndarray, nearshore: np.ndarray) -> dict[str, int]:
    near = int(np.count_nonzero(mask & nearshore))
    off = int(np.count_nonzero(mask & ~nearshore))
    return {"nearshore": near, "offshore": off, "total": near + off}


def lat_lon_to_glorys_indices(
    lat: float,
    lon: float,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
) -> tuple[int, int]:
    lat_a = np.array([[lat]], dtype=float)
    lon_a = np.array([[lon]], dtype=float)
    j_idx, i_idx = assign_glorys_cell_indices(lat_a, lon_a, lat_dst, lon_dst)
    return int(j_idx[0, 0]), int(i_idx[0, 0])


@dataclass
class CoverageAccumulator:
    """Union of per-day harmonization gaps across the overlap run."""

    lat_dst: np.ndarray
    lon_dst: np.ndarray
    nearshore: np.ndarray
    depth_grid_m: np.ndarray
    min_wet_fraction: float
    level_masks: dict[str, np.ndarray] = field(default_factory=dict)

    def observe_day(
        self,
        gridded: WcofsGlorysGrid,
        z_levels: np.ndarray,
        thetao: np.ndarray,
    ) -> None:
        for spec in COVERAGE_LEVEL_SPECS:
            gap = harmonization_gap_mask(
                gridded,
                z_levels,
                thetao,
                spec.depth_m,
                min_wet_fraction=self.min_wet_fraction,
            )
            if spec.name not in self.level_masks:
                self.level_masks[spec.name] = np.zeros_like(gap, dtype=bool)
            self.level_masks[spec.name] |= gap

    def cell_counts(self) -> dict[str, dict[str, int]]:
        return {
            name: _count_cells(mask, self.nearshore)
            for name, mask in self.level_masks.items()
        }


def load_cufes_event_index(path: Path | None = None) -> pd.DataFrame:
    """
    Load CUFES ``event_id`` rows for coverage attribution.

    CSV columns: ``event_id``, ``start_latitude``, ``start_longitude``,
    ``stop_latitude``, ``stop_longitude``, optional ``in_reduced_set`` (0/1).
    """
    path = Path(path) if path is not None else DEFAULT_CUFES_FIXTURE
    if not path.is_file():
        raise FileNotFoundError(f"CUFES coverage fixture not found: {path}")
    return pd.read_csv(path)


def count_cufes_events_in_gap_cells(
    events: pd.DataFrame,
    gap_mask: np.ndarray,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    *,
    expected_kept: int,
    expected_reduced: int,
) -> dict[str, Any]:
    in_gap_kept = 0
    in_gap_reduced = 0
    for _, row in events.iterrows():
        lat, lon = event_midpoint_lat_lon(row)
        if not np.isfinite(lat):
            continue
        j, i = lat_lon_to_glorys_indices(lat, lon, lat_dst, lon_dst)
        if j < 0 or i < 0 or j >= gap_mask.shape[0] or i >= gap_mask.shape[1]:
            continue
        if not gap_mask[j, i]:
            continue
        in_gap_kept += 1
        if bool(row.get("in_reduced_set", 0)):
            in_gap_reduced += 1
    return {
        "events_in_fixture": int(len(events)),
        "expected_kept_event_count": int(expected_kept),
        "expected_reduced_event_count": int(expected_reduced),
        "in_gap_cells_kept_fixture": in_gap_kept,
        "in_gap_cells_reduced_fixture": in_gap_reduced,
    }


def build_coverage_report(
    accumulator: CoverageAccumulator,
    *,
    cufes_events: pd.DataFrame | None = None,
    expected_kept: int = 14592,
    expected_reduced: int = 13326,
) -> dict[str, Any]:
    cell_counts = accumulator.cell_counts()
    cufes_by_level: dict[str, Any] = {}
    if cufes_events is not None and not cufes_events.empty:
        for name, mask in accumulator.level_masks.items():
            cufes_by_level[name] = count_cufes_events_in_gap_cells(
                cufes_events,
                mask,
                accumulator.lat_dst,
                accumulator.lon_dst,
                expected_kept=expected_kept,
                expected_reduced=expected_reduced,
            )
    return {
        "schema_version": "wcofs_glorys_coverage_v1",
        "min_wet_fraction": accumulator.min_wet_fraction,
        "levels": [
            {
                "name": spec.name,
                "depth_m": spec.depth_m,
                "glorys_ocean_wcofs_insufficient_cells": cell_counts.get(spec.name, {}),
                "cufes_events": cufes_by_level.get(spec.name),
            }
            for spec in COVERAGE_LEVEL_SPECS
        ],
    }


def write_coverage_cells_csv(
    accumulator: CoverageAccumulator,
    path: Path,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    nj, ni = accumulator.nearshore.shape
    lat2d, lon2d = np.meshgrid(accumulator.lat_dst, accumulator.lon_dst, indexing="ij")
    rows: list[dict[str, Any]] = []
    for spec in COVERAGE_LEVEL_SPECS:
        mask = accumulator.level_masks.get(spec.name)
        if mask is None:
            continue
        for j in range(nj):
            for i in range(ni):
                if not mask[j, i]:
                    continue
                rows.append(
                    {
                        "level": spec.name,
                        "depth_m": spec.depth_m,
                        "glorys_j": j,
                        "glorys_i": i,
                        "lat": float(lat2d[j, i]),
                        "lon": float(lon2d[j, i]),
                        "nearshore": bool(accumulator.nearshore[j, i]),
                    }
                )
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def write_coverage_report(
    report: dict[str, Any],
    *,
    json_path: Path | None = None,
    csv_path: Path | None = None,
    accumulator: CoverageAccumulator | None = None,
) -> tuple[Path, Path | None]:
    json_path = Path(json_path) if json_path is not None else DEFAULT_REPORT_JSON
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    csv_out: Path | None = None
    if csv_path is not None and accumulator is not None:
        csv_out = write_coverage_cells_csv(accumulator, csv_path)
    return json_path, csv_out


def coverage_paths_from_config(config: dict[str, Any]) -> dict[str, Path]:
    block = config.get("coverage_report") or {}
    return {
        "json": REPO_ROOT / str(block.get("json_path", DEFAULT_REPORT_JSON.relative_to(REPO_ROOT))),
        "csv": REPO_ROOT / str(
            block.get("csv_path", DEFAULT_REPORT_CSV.relative_to(REPO_ROOT))
        ),
        "cufes_fixture": REPO_ROOT
        / str(block.get("cufes_events_fixture", DEFAULT_CUFES_FIXTURE.relative_to(REPO_ROOT))),
    }


def expected_cufes_counts(config: dict[str, Any]) -> tuple[int, int]:
    block = config.get("coverage_report") or {}
    return (
        int(block.get("expected_kept_event_count", 14592)),
        int(block.get("expected_reduced_event_count", 13326)),
    )
