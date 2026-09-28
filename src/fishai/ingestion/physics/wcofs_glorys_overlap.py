"""
Pair WCOFS daily ``avg.nowcast`` with GLORYS daily means on the pilot overlap window.

Network downloads are orchestrated here but never run in CI (inject ``fetch_*`` mocks).
"""

from __future__ import annotations

import datetime as dt
import json
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
import xarray as xr

from fishai.ingestion.copernicus_compliance import append_pull_log, build_pull_record
from fishai.ingestion.physics.coast_distance import nearshore_mask, shoreline_path_from_config
from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.sources.glorys import (
    glorys_column_features,
    resolve_glorys_product_id,
)
from fishai.ingestion.physics.wcofs_glorys_coverage import (
    CoverageAccumulator,
    build_coverage_report,
    coverage_paths_from_config,
    expected_cufes_counts,
    load_cufes_event_index,
    write_coverage_report,
)
from fishai.ingestion.physics.wcofs_glorys_grid import (
    coarsen_wcofs_to_glorys,
    compute_wcofs_covariates_on_glorys_grid,
    min_wet_fraction_from_config,
)
from fishai.ingestion.physics.wcofs_pull_log import append_wcofs_pull_log, build_wcofs_pull_record
from fishai.ingestion.physics.wcofs_pds_store import open_wcofs_cycle
from fishai.ingestion.sources import REPO_ROOT, attribution_for

DEFAULT_CONFIG = REPO_ROOT / "data" / "config" / "wcofs_glorys_overlap.yaml"


class DailyRequestBudgetExceeded(RuntimeError):
    """Raised when the configured daily HTTP request cap is exceeded."""


class _DailyRequestBudget:
    def __init__(self, max_per_day: int) -> None:
        self._max = int(max_per_day)
        self._day: dt.date | None = None
        self._count = 0

    def charge(self, when: dt.date | None = None, n: int = 1) -> None:
        today = when or dt.date.today()
        if self._day != today:
            self._day = today
            self._count = 0
        self._count += int(n)
        if self._count > self._max:
            raise DailyRequestBudgetExceeded(f"exceeded {self._max} requests on {today}")


def load_overlap_config(path: Path | str | None = None) -> dict[str, Any]:
    cfg_path = Path(path) if path is not None else DEFAULT_CONFIG
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8"))


def _config_date(value: Any) -> dt.date:
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def overlap_dates(config: dict[str, Any]) -> list[dt.date]:
    start = _config_date(config["overlap"]["start"])
    end = _config_date(config["overlap"]["end"])
    days: list[dt.date] = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur += dt.timedelta(days=1)
    return days


def split_label(day: dt.date, config: dict[str, Any]) -> str:
    fit_end = _config_date(config["split"]["fit_end"])
    test_start = _config_date(config["split"]["test_start"])
    if day <= fit_end:
        return "fit"
    if day >= test_start:
        return "test"
    return "holdout"


def meteorological_season(day: dt.date) -> str:
    month = day.month
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "fall"


def depth_grid_m(config: dict[str, Any]) -> np.ndarray:
    spec = config["depth_grid_m"]
    start = int(spec["start"])
    end = int(spec["end"])
    step = int(spec["step"])
    return np.arange(start, end + step, step, dtype=float)


def glorys_grid_from_config(config: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    bbox = config["pilot_bbox"]
    return glorys_target_grid(
        float(bbox["lat_min"]),
        float(bbox["lat_max"]),
        float(bbox["lon_min"]),
        float(bbox["lon_max"]),
    )


def wcofs_covariate_arrays_on_glorys_grid(
    ds_wcofs: xr.Dataset,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    config: dict[str, Any],
) -> dict[str, np.ndarray]:
    """Shared WCOFS covariates on the GLORYS grid (overlap uses ``wcofs_`` prefixes in rows)."""
    depth = depth_grid_m(config)
    gridded = coarsen_wcofs_to_glorys(
        ds_wcofs,
        lat_dst,
        lon_dst,
        depth,
        min_wet_fraction=min_wet_fraction_from_config(config),
    )
    return compute_wcofs_covariates_on_glorys_grid(gridded)


def glorys_profiles_on_depth_grid(
    z_levels: np.ndarray,
    temp: np.ndarray,
    salt: np.ndarray,
    depth_grid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(z_levels)
    z_sorted = z_levels[order]
    t_sorted = temp[order]
    s_sorted = salt[order]
    return (
        np.interp(depth_grid, z_sorted, t_sorted, left=np.nan, right=np.nan),
        np.interp(depth_grid, z_sorted, s_sorted, left=np.nan, right=np.nan),
    )


def pair_day_cell(
    day: dt.date,
    j: int,
    i: int,
    lat: float,
    lon: float,
    wcofs_metrics: dict[str, float],
    glorys_metrics: dict[str, float],
    wcofs_surface: dict[str, float],
    glorys_surface: dict[str, float],
    *,
    config: dict[str, Any],
    nearshore: bool,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "day": day.isoformat(),
        "glorys_j": j,
        "glorys_i": i,
        "lat": lat,
        "lon": lon,
        "split": split_label(day, config),
        "season": meteorological_season(day),
        "nearshore": bool(nearshore),
        **wcofs_metrics,
        **glorys_metrics,
        **wcofs_surface,
        **glorys_surface,
    }
    return row


def build_overlap_metadata(config: dict[str, Any]) -> dict[str, Any]:
    glorys_cfg = config["glorys"]
    shore = config.get("shoreline", {})
    return {
        "schema_version": "wcofs_glorys_overlap_v1",
        "overlap_start": config["overlap"]["start"],
        "overlap_end": config["overlap"]["end"],
        "expected_days": int(config["overlap"]["expected_days"]),
        "glorys_product_id": glorys_cfg["product_id"],
        "glorys_production_status": glorys_cfg["production_status"],
        "glorys_copernicus_doi": glorys_cfg["copernicus_doi"],
        "shoreline_path": str(shoreline_path_from_config(config)),
        "natural_earth_version": shore.get("natural_earth_version"),
        "wcofs_attribution": attribution_for("wcofs"),
        "glorys_attribution": attribution_for("glorys"),
    }


def write_overlap_parquet(df: pd.DataFrame, path: Path, metadata: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    meta_json = json.dumps(metadata, sort_keys=True)
    df.to_parquet(path, index=False, custom_metadata={"overlap": meta_json.encode()})
    return path


def overlap_day_dataframe(
    day: dt.date,
    wcofs_fields: dict[str, np.ndarray],
    glorys_thetao: np.ndarray,
    glorys_so: np.ndarray,
    z_levels: np.ndarray,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    nearshore: np.ndarray,
    *,
    config: dict[str, Any],
) -> pd.DataFrame:
    """One day of overlap rows on the GLORYS pilot grid."""
    rows: list[dict[str, Any]] = []
    for j, la in enumerate(lat_dst):
        for i, lo in enumerate(lon_dst):
            wcofs_metrics = {f"wcofs_{k}": float(wcofs_fields[k][j, i]) for k in wcofs_fields}
            glorys_metrics = {
                f"glorys_{k}": v
                for k, v in glorys_column_features(
                    z_levels, glorys_thetao[:, j, i], glorys_so[:, j, i], None
                ).items()
                if k != "mlotst_crosscheck"
            }
            wcofs_surface = {
                "wcofs_sst_grad": wcofs_metrics["wcofs_sst_grad"],
                "wcofs_front_distance_km": wcofs_metrics["wcofs_front_distance_km"],
            }
            glorys_surface = {
                "glorys_sst_grad": float("nan"),
                "glorys_front_distance_km": float("nan"),
            }
            rows.append(
                pair_day_cell(
                    day,
                    j,
                    i,
                    float(la),
                    float(lo),
                    wcofs_metrics,
                    glorys_metrics,
                    wcofs_surface,
                    glorys_surface,
                    config=config,
                    nearshore=bool(nearshore[j, i]),
                )
            )
    return pd.DataFrame(rows)


def pair_overlap_from_synthetic(
    day: dt.date,
    wcofs_slab: xr.Dataset,
    glorys_thetao: np.ndarray,
    glorys_so: np.ndarray,
    z_levels: np.ndarray,
    lat_dst: np.ndarray,
    lon_dst: np.ndarray,
    *,
    config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Test helper: one day, full GLORYS subgrid."""
    config = config or load_overlap_config()
    wcofs_fields = wcofs_covariate_arrays_on_glorys_grid(wcofs_slab, lat_dst, lon_dst, config)
    lat2d, lon2d = np.meshgrid(lat_dst, lon_dst, indexing="ij")
    nearshore = nearshore_mask(lat2d, lon2d, config=config)
    return overlap_day_dataframe(
        day,
        wcofs_fields,
        glorys_thetao,
        glorys_so,
        z_levels,
        lat_dst,
        lon_dst,
        nearshore,
        config=config,
    )


def run_overlap_pairing(
    *,
    config: dict[str, Any] | None = None,
    days: Sequence[dt.date] | None = None,
    wcofs_open: Callable[[dt.date], xr.Dataset] | None = None,
    glorys_fetch: Callable[[dt.date], dict[str, Any]] | None = None,
    budget: _DailyRequestBudget | None = None,
    wcofs_log: Path | None = None,
    glorys_log: Path | None = None,
    output_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Build the overlap table (live downloads when ``wcofs_open`` / ``glorys_fetch`` omitted).

    GLORYS subsets must be requested server-side (Copernicus Marine toolbox); inject
    ``glorys_fetch`` in tests.
    """
    config = config or load_overlap_config()
    days = list(days) if days is not None else overlap_dates(config)
    expected = int(config["overlap"]["expected_days"])
    if days is not None and len(days) == expected and len(overlap_dates(config)) != expected:
        raise ValueError("configured overlap.expected_days does not match date span")
    lat_dst, lon_dst = glorys_grid_from_config(config)
    depth_grid = depth_grid_m(config)
    min_wf = min_wet_fraction_from_config(config)
    lat2d, lon2d = np.meshgrid(lat_dst, lon_dst, indexing="ij")
    nearshore = nearshore_mask(lat2d, lon2d, config=config)
    coverage_accumulator = CoverageAccumulator(
        lat_dst, lon_dst, nearshore, depth_grid, min_wf
    )
    rate = config.get("rate_limits") or {}
    budget = budget or _DailyRequestBudget(int(rate.get("max_requests_per_day", 200)))
    wcofs_log = wcofs_log or REPO_ROOT / str(config["pull_logs"]["wcofs"])
    glorys_log = glorys_log or REPO_ROOT / str(config["pull_logs"]["glorys"])
    all_rows: list[dict[str, Any]] = []
    for day in days:
        if wcofs_open is None:
            budget.charge(day, 1)
            ds = open_wcofs_cycle(day, product="avg_nowcast")
        else:
            ds = wcofs_open(day)
        key = str(ds.attrs.get("wcofs_s3_key", ""))
        append_wcofs_pull_log(
            build_wcofs_pull_record(
                cycle_date=day.isoformat(),
                s3_key=key,
                attribution=attribution_for("wcofs"),
            ),
            log_path=wcofs_log,
        )
        if glorys_fetch is None:
            raise RuntimeError("glorys_fetch is required for live overlap pairing")
        budget.charge(day, 1)
        glorys_payload = glorys_fetch(day)
        glorys_dataset_id = resolve_glorys_product_id(day, config)
        append_pull_log(
            build_pull_record(
                dataset_id=glorys_dataset_id,
                date_start=day.isoformat(),
                date_end=day.isoformat(),
                variables=("thetao", "so"),
                bbox=(
                    float(config["pilot_bbox"]["lat_min"]),
                    float(config["pilot_bbox"]["lat_max"]),
                    float(config["pilot_bbox"]["lon_min"]),
                    float(config["pilot_bbox"]["lon_max"]),
                ),
            ),
            log_path=glorys_log,
        )
        gridded = coarsen_wcofs_to_glorys(
            ds, lat_dst, lon_dst, depth_grid, min_wet_fraction=min_wf
        )
        coverage_accumulator.observe_day(
            gridded, glorys_payload["depth"], glorys_payload["thetao"]
        )
        wcofs_fields = compute_wcofs_covariates_on_glorys_grid(gridded)
        frame = overlap_day_dataframe(
            day,
            wcofs_fields,
            glorys_payload["thetao"],
            glorys_payload["so"],
            glorys_payload["depth"],
            lat_dst,
            lon_dst,
            nearshore,
            config=config,
        )
        all_rows.extend(frame.to_dict(orient="records"))
    df = pd.DataFrame(all_rows)
    metadata = build_overlap_metadata(config)
    metadata["glorys_production_status"] = str(config["glorys"]["production_status"])
    cov_paths = coverage_paths_from_config(config)
    kept_n, reduced_n = expected_cufes_counts(config)
    try:
        cufes_index = load_cufes_event_index(cov_paths["cufes_fixture"])
    except FileNotFoundError:
        cufes_index = None
    coverage_report = build_coverage_report(
        coverage_accumulator,
        cufes_events=cufes_index,
        expected_kept=kept_n,
        expected_reduced=reduced_n,
    )
    json_path, _csv_path = write_coverage_report(
        coverage_report,
        json_path=cov_paths["json"],
        csv_path=cov_paths["csv"],
        accumulator=coverage_accumulator,
    )
    try:
        metadata["coverage_report_json"] = str(json_path.relative_to(REPO_ROOT))
    except ValueError:
        metadata["coverage_report_json"] = str(json_path)
    if output_path is not None:
        write_overlap_parquet(df, output_path, metadata)
    return df, metadata
