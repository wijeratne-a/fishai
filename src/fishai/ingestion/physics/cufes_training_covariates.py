"""Build CUFES training covariates from Copernicus GLORYS (event_id join only)."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from collections import defaultdict
from collections.abc import Callable, Iterable, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from fishai.ingestion.copernicus_compliance import (
    GLORYS_CREDIT_TEXT,
    GLORYS_DOI,
    append_pull_log,
    build_pull_record,
    require_glorys_attribution,
)
from fishai.ingestion.physics.bathymetry import (
    WCOFS_BOTTOM_DEPTH_SOURCE,
    WCOFS_BOTTOM_DEPTH_VARIABLE,
    glorys_pilot_depth_grid,
    normalize_lon_for_axis,
    sample_wcofs_h_bottom_depth_m,
)
from fishai.ingestion.physics.covariates import (
    COL_EVENT_ID,
    COL_START_LAT,
    COL_START_LON,
    COL_STOP_LAT,
    COL_STOP_LON,
    CUFES_COVARIATE_FIELDS,
    DEFAULT_GRID_CELL_KM,
    DROP_REASON_OUTSIDE_WCOFS_DOMAIN,
    DROP_REASON_WCOFS_LOW_WET_FRACTION,
    DROP_TABLE_COLUMNS,
    endpoints_present,
    event_mid_time,
    event_midpoint_lat_lon,
    great_circle_sample_points,
    join_covariates_to_events,
    normalize_cufes_events_for_physics,
)
from fishai.ingestion.physics.features import (
    front_distance_km,
    sst_gradient,
    upwelling_covariate_metadata,
)
from fishai.ingestion.physics.sources.glorys import (
    VARIABLES,
    glorys_column_features,
    glorys_product_for_date,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import (
    coarsen_min_wet_fraction,
    load_overlap_config,
)
from fishai.ingestion.physics.wind_pull_log import (
    append_wind_pull_log,
    build_upwelling_wind_status_record,
)
from fishai.ingestion.physics.wind_shared_forcing import (
    UPWELLING_STATUS_NO_CONSISTENT_WIND,
    UPWELLING_WIND_FORCING_ENABLED,
    wind_product_audit_summary,
)
from fishai.ingestion.physics.wcofs_h_glorys_store import (
    DEFAULT_MANIFEST_REL,
    MODEL_FLOOR_TOLERANCE_M,
    WcofsHGlorysGrid,
    depth_at_model_floor,
    load_wcofs_h_manifest,
)
from fishai.ingestion.sources import REPO_ROOT, attribution_for, require_approved

DEFAULT_EVENTS_PATH = REPO_ROOT / "data" / "processed" / "calcofi_cufes" / "cufes_events.parquet"
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT / "data" / "processed" / "calcofi_cufes" / "cufes_training_covariates.parquet"
)
DEFAULT_DROPS_NAME = "cufes_training_covariate_drops.parquet"
DEFAULT_DROP_SUMMARY_NAME = "cufes_training_covariate_drop_summary.json"

PILOT_BBOX = (32.0, 35.0, -121.0, -117.0)

TRAINING_OUTPUT_COLUMNS: tuple[str, ...] = (
    COL_EVENT_ID,
    *CUFES_COVARIATE_FIELDS,
    "upwelling_status",
    "bottom_depth_m",
    "depth_at_model_floor",
    "source",
    "provenance",
    "excluded",
    "source_product",
    "excluded_reason",
)


def bottom_depth_metadata(
    config: dict[str, Any],
    *,
    store: GlorysFieldStore | None = None,
) -> dict[str, Any]:
    bathy = config.get("bathymetry") or {}
    manifest_doc: dict[str, Any] = {}
    try:
        manifest_doc = load_wcofs_h_manifest()
    except (FileNotFoundError, json.JSONDecodeError):
        manifest_doc = {"manifest_path": DEFAULT_MANIFEST_REL, "build_status": "manifest_only"}
    block: dict[str, Any] = {
        "source": WCOFS_BOTTOM_DEPTH_SOURCE,
        "variable": WCOFS_BOTTOM_DEPTH_VARIABLE,
        "grid": bathy.get("grid", "glorys_1_12deg"),
        "coarsen": bathy.get("coarsen", "area_weighted_wet_masked"),
        "min_wet_fraction": coarsen_min_wet_fraction(config),
        "artifact_manifest": DEFAULT_MANIFEST_REL,
        "model_floor_tolerance_m": MODEL_FLOOR_TOLERANCE_M,
    }
    if store is not None:
        block["roms_hmin_m"] = store.roms_hmin_m
        block["hmin_source"] = store.hmin_source
    elif manifest_doc.get("roms_hmin_m") is not None:
        block["roms_hmin_m"] = manifest_doc["roms_hmin_m"]
        block["hmin_source"] = manifest_doc.get("hmin_source")
    if manifest_doc.get("sha256"):
        block["artifact_sha256"] = manifest_doc["sha256"]
        block["artifact_path"] = manifest_doc.get("artifact_path")
    return {"bottom_depth_m": block}


@dataclass(frozen=True)
class GlorysSubsetBatch:
    dataset_id: str
    date_start: dt.date
    date_end: dt.date
    variables: tuple[str, ...]
    bbox: tuple[float, float, float, float]


@dataclass
class GlorysDayFields:
    """One day of GLORYS fields on the pilot 1/12° grid."""

    day: dt.date
    dataset_id: str
    lat: np.ndarray
    lon: np.ndarray
    depth_levels: np.ndarray
    thetao: np.ndarray
    so: np.ndarray
    mlotst: np.ndarray
    u10: np.ndarray
    v10: np.ndarray
    sst_grad: np.ndarray
    front_distance_km: np.ndarray
    upwelling: np.ndarray


@dataclass
class GlorysFieldStore:
    """In-memory GLORYS grids keyed by calendar day plus static WCOFS ``h`` on the GLORYS grid."""

    wcofs_h_m: np.ndarray
    has_source: np.ndarray
    wet_fraction: np.ndarray
    min_wet_fraction: float
    roms_hmin_m: float
    hmin_source: str
    lat: np.ndarray
    lon: np.ndarray
    wind_source_id: str = "ccmp_winds"
    days: dict[dt.date, GlorysDayFields] = field(default_factory=dict)

    @classmethod
    def from_wcofs_h_grid(cls, grid: WcofsHGlorysGrid) -> GlorysFieldStore:
        return cls(
            wcofs_h_m=grid.h_m,
            has_source=grid.has_source,
            wet_fraction=grid.wet_fraction,
            min_wet_fraction=grid.min_wet_fraction,
            roms_hmin_m=grid.roms_hmin_m,
            hmin_source=grid.hmin_source,
            lat=grid.lat,
            lon=grid.lon,
        )

    def field_sampler(self, lat: float, lon: float, when: pd.Timestamp) -> dict[str, Any]:
        if pd.isna(when):
            return {f: float("nan") for f in CUFES_COVARIATE_FIELDS}
        day = when.date()
        fields = self.days.get(day)
        if fields is None:
            return {f: float("nan") for f in CUFES_COVARIATE_FIELDS}
        j, i = _nearest_cell(lat, lon, fields.lat, fields.lon)
        depth = fields.depth_levels
        feats = glorys_column_features(
            depth,
            fields.thetao[:, j, i],
            fields.so[:, j, i],
            float(fields.mlotst[j, i]),
        )
        out = {k: feats[k] for k in CUFES_COVARIATE_FIELDS if k in feats}
        out["sst_grad"] = float(fields.sst_grad[j, i])
        out["front_distance_km"] = float(fields.front_distance_km[j, i])
        out["upwelling"] = float("nan")
        return out

    def sample_bottom_depth_with_reason(self, lat: float, lon: float) -> tuple[float, str | None]:
        return sample_wcofs_h_bottom_depth_m(
            lat,
            lon,
            self.wcofs_h_m,
            self.lat,
            self.lon,
            has_source=self.has_source,
            wet_fraction=self.wet_fraction,
            min_wet_fraction=self.min_wet_fraction,
        )


def _nearest_cell(lat: float, lon: float, lat_axis: np.ndarray, lon_axis: np.ndarray) -> tuple[int, int]:
    lon = normalize_lon_for_axis(lon, lon_axis)
    j = int(np.argmin(np.abs(lat_axis - lat)))
    i = int(np.argmin(np.abs(lon_axis - lon)))
    return j, i


def mean_bottom_depth_m_along_segment(
    event: pd.Series,
    store: GlorysFieldStore,
    *,
    grid_cell_km: float = DEFAULT_GRID_CELL_KM,
) -> tuple[float, list[str]]:
    """Segment mean of WCOFS ``h`` on the GLORYS grid (same track sampling as GLORYS covariates)."""
    if not endpoints_present(event):
        return float("nan"), []
    lat0, lon0 = float(event[COL_START_LAT]), float(event[COL_START_LON])
    lat1, lon1 = float(event[COL_STOP_LAT]), float(event[COL_STOP_LON])
    points = great_circle_sample_points(lat0, lon0, lat1, lon1, grid_cell_km=grid_cell_km)
    depths: list[float] = []
    reasons: list[str] = []
    for lat, lon in points:
        val, reason = store.sample_bottom_depth_with_reason(lat, lon)
        if reason is not None:
            reasons.append(reason)
            continue
        if np.isfinite(val):
            depths.append(float(val))
    if not depths:
        return float("nan"), sorted(set(reasons)) if reasons else [DROP_REASON_WCOFS_LOW_WET_FRACTION]
    return float(np.mean(depths)), []


def unique_event_days(events: pd.DataFrame) -> list[dt.date]:
    days: set[dt.date] = set()
    for _, row in events.iterrows():
        mid = event_mid_time(row)
        if pd.isna(mid):
            continue
        days.add(mid.date())
    return sorted(days)


def plan_glorys_subset_batches(
    days: Sequence[dt.date],
    *,
    bbox: tuple[float, float, float, float] = PILOT_BBOX,
    variables: tuple[str, ...] = VARIABLES,
) -> list[GlorysSubsetBatch]:
    """Group unique event days into monthly Copernicus subset requests per dataset id."""
    by_key: dict[tuple[str, int, int], list[dt.date]] = defaultdict(list)
    for day in days:
        product_id = glorys_product_for_date(day)
        by_key[(product_id, day.year, day.month)].append(day)
    batches: list[GlorysSubsetBatch] = []
    for (product_id, _year, _month), month_days in sorted(by_key.items()):
        month_days = sorted(month_days)
        batches.append(
            GlorysSubsetBatch(
                dataset_id=product_id,
                date_start=month_days[0],
                date_end=month_days[-1],
                variables=variables,
                bbox=bbox,
            )
        )
    return batches


def _compute_day_surface_fields(
    day: dt.date,
    dataset_id: str,
    lat: np.ndarray,
    lon: np.ndarray,
    depth_levels: np.ndarray,
    thetao: np.ndarray,
    so: np.ndarray,
    mlotst: np.ndarray,
) -> GlorysDayFields:
    sst = thetao[0]
    grad = sst_gradient(sst, lat, lon)
    lat2d, lon2d = np.meshgrid(lat, lon, indexing="ij")
    front_km = front_distance_km(grad, lat2d, lon2d)
    nj, ni = lat.size, lon.size
    upwelling = np.full((nj, ni), np.nan, dtype=float)
    return GlorysDayFields(
        day=day,
        dataset_id=dataset_id,
        lat=lat,
        lon=lon,
        depth_levels=depth_levels,
        thetao=thetao,
        so=so,
        mlotst=mlotst,
        u10=np.full((nj, ni), np.nan, dtype=float),
        v10=np.full((nj, ni), np.nan, dtype=float),
        sst_grad=grad,
        front_distance_km=front_km,
        upwelling=upwelling,
    )


def build_synthetic_day_fields(
    day: dt.date,
    lat: np.ndarray,
    lon: np.ndarray,
    *,
    nz: int = 5,
) -> GlorysDayFields:
    """Test helper: constant profiles and winds."""
    if nz == 5:
        depth_levels = np.array([50.0, 20.0, 10.0, 5.0, 0.0])
        base_temp = np.array([10.0, 15.0, 17.8, 17.9, 18.0])
    else:
        depth_levels = np.linspace(0.0, 50.0, nz)
        base_temp = 18.5 - 0.12 * depth_levels
    nj, ni = lat.size, lon.size
    lat2d = lat[:, None] + np.zeros((nj, ni))
    lon2d = lon[None, :] + np.zeros((nj, ni))
    thetao = np.stack(
        [
            base_temp[k] + 0.03 * lat2d + 0.01 * lon2d
            for k in range(depth_levels.size)
        ],
        axis=0,
    )
    so = np.stack(
        [33.5 + 0.0005 * lat2d for _ in range(depth_levels.size)],
        axis=0,
    )
    mlotst = np.full((nj, ni), 20.0)
    product_id = glorys_product_for_date(day)
    return _compute_day_surface_fields(
        day,
        product_id,
        lat,
        lon,
        depth_levels,
        thetao,
        so,
        mlotst,
    )


def _excluded_reason_map(drops: pd.DataFrame) -> dict[Any, str]:
    if drops.empty:
        return {}
    out: dict[Any, str] = {}
    for eid, grp in drops.groupby("event_id"):
        reasons = sorted(set(grp["reason"].astype(str)))
        out[eid] = ";".join(reasons)
    return out


def _apply_exclusion_state(out: pd.DataFrame, drops: pd.DataFrame) -> pd.DataFrame:
    excluded_ids: set[Any] = set(drops["event_id"].unique()) if not drops.empty else set()
    out = out.copy()
    out["excluded"] = out[COL_EVENT_ID].isin(excluded_ids)
    if excluded_ids:
        for col in CUFES_COVARIATE_FIELDS:
            out.loc[out["excluded"], col] = np.nan
        out.loc[out["excluded"], "bottom_depth_m"] = np.nan
        if "depth_at_model_floor" in out.columns:
            out.loc[out["excluded"], "depth_at_model_floor"] = False
    return out


def attach_bottom_depth_and_reasons(
    events: pd.DataFrame,
    covariates: pd.DataFrame,
    drops: pd.DataFrame,
    store: GlorysFieldStore,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Add ``bottom_depth_m``, ``source_product``, ``excluded_reason``; extend drops if needed."""
    drop_rows = drops.to_dict(orient="records")
    bottom_depth: list[float] = []
    at_floor: list[bool] = []
    source_products: list[str] = []
    for _, event in events.iterrows():
        eid = event[COL_EVENT_ID]
        mid_lat, mid_lon = event_midpoint_lat_lon(event)
        mid_t = event_mid_time(event)
        if pd.isna(mid_t):
            product_id = ""
            depth_val = float("nan")
            depth_reasons: list[str] = []
            floor_flag = False
        else:
            product_id = glorys_product_for_date(mid_t.date())
            depth_val, depth_reasons = mean_bottom_depth_m_along_segment(event, store)
            floor_flag = depth_at_model_floor(depth_val, store.roms_hmin_m)
        source_products.append(product_id)
        bottom_depth.append(depth_val)
        at_floor.append(floor_flag)
        if not np.isfinite(depth_val) or depth_val <= 0.0:
            reasons = depth_reasons or [DROP_REASON_WCOFS_LOW_WET_FRACTION]
            for reason in sorted(set(reasons)):
                drop_rows.append(
                    {
                        "event_id": eid,
                        "reason": reason,
                        "covariate": "bottom_depth_m",
                        "latitude": mid_lat,
                        "longitude": mid_lon,
                    }
                )
    out = covariates.copy()
    out["bottom_depth_m"] = bottom_depth
    out["depth_at_model_floor"] = at_floor
    out["source_product"] = source_products
    drops_out = pd.DataFrame(drop_rows, columns=list(DROP_TABLE_COLUMNS))
    out = _apply_exclusion_state(out, drops_out)
    reasons = _excluded_reason_map(drops_out)
    out["excluded_reason"] = out[COL_EVENT_ID].map(lambda e: reasons.get(e, ""))
    out.loc[~out["excluded"], "excluded_reason"] = ""
    return out, drops_out


def write_training_covariates_parquet(
    df: pd.DataFrame,
    path: Path,
    *,
    entry: dict[str, Any],
    config: dict[str, Any] | None = None,
    store: GlorysFieldStore | None = None,
) -> Path:
    import pyarrow as pa
    import pyarrow.parquet as pq

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cfg = config or load_overlap_config()
    metadata = {
        "attribution": attribution_for("glorys"),
        "glorys_derived": True,
        "copernicus_doi": GLORYS_DOI,
        "copernicus_credit": GLORYS_CREDIT_TEXT,
        **bottom_depth_metadata(cfg, store=store),
        **upwelling_covariate_metadata(store.wind_source_id if store else "ccmp_winds"),
    }
    require_glorys_attribution(metadata)
    meta_json = json.dumps(metadata, sort_keys=True)
    table = pa.Table.from_pandas(df, preserve_index=False)
    custom = dict(table.schema.metadata or {})
    custom["glorys"] = meta_json.encode()
    table = table.replace_schema_metadata(custom)
    pq.write_table(table, path)
    return path


def apply_upwelling_wind_policy(out: pd.DataFrame) -> pd.DataFrame:
    """NaN ``upwelling`` with status metadata when no consistent wind product is wired."""
    out = out.copy()
    if UPWELLING_WIND_FORCING_ENABLED:
        if "upwelling_status" not in out.columns:
            out["upwelling_status"] = ""
        return out
    out["upwelling"] = np.nan
    out["upwelling_status"] = UPWELLING_STATUS_NO_CONSISTENT_WIND
    return out


def record_upwelling_wind_status_pull_log(
    *,
    log_path: Path | None = None,
) -> Path:
    cfg = load_overlap_config()
    path = log_path or REPO_ROOT / str(
        cfg["pull_logs"].get("winds", "data/provenance/wind_pull_log.jsonl")
    )
    return append_wind_pull_log(
        build_upwelling_wind_status_record(
            upwelling_status=UPWELLING_STATUS_NO_CONSISTENT_WIND,
            audit=wind_product_audit_summary(),
            wind_fetch_performed=False,
        ),
        log_path=path,
    )


def build_cufes_training_covariates_table(
    events: pd.DataFrame,
    store: GlorysFieldStore,
    *,
    source: str = "glorys",
    provenance: str = "",
    drops_parquet_path: Path | None = None,
    drop_summary_json_path: Path | None = None,
    wind_status_log_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame, dict[str, Any]]:
    """Join GLORYS covariates to QC-kept CUFES events (one row per ``event_id``)."""
    cov, qc, drops = join_covariates_to_events(
        events,
        field_sampler=store.field_sampler,
        source=source,
        provenance=provenance,
        drops_parquet_path=drops_parquet_path,
        drop_summary_json_path=drop_summary_json_path,
    )
    out, drops = attach_bottom_depth_and_reasons(events, cov, drops, store)
    out = apply_upwelling_wind_policy(out)
    if not UPWELLING_WIND_FORCING_ENABLED:
        record_upwelling_wind_status_pull_log(log_path=wind_status_log_path)
    for col in TRAINING_OUTPUT_COLUMNS:
        if col not in out.columns:
            raise ValueError(f"missing output column: {col}")
    out = out[list(TRAINING_OUTPUT_COLUMNS)]
    floor_qc = {
        "depth_at_model_floor_count": int(out["depth_at_model_floor"].sum()),
        "depth_at_model_floor_computed_at_run_time": True,
        "roms_hmin_m": store.roms_hmin_m,
        "hmin_source": store.hmin_source,
    }
    return out, qc, drops, floor_qc


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _subset_batch_live(
    batch: GlorysSubsetBatch,
    output_dir: Path,
    *,
    log_path: Path,
) -> Path:
    try:
        import copernicusmarine  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - runtime host only
        raise RuntimeError("copernicusmarine package required for live GLORYS subset") from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / (
        f"{batch.dataset_id}_{batch.date_start.isoformat()}_{batch.date_end.isoformat()}.nc"
    )
    la0, la1, lo0, lo1 = batch.bbox
    copernicusmarine.subset(
        dataset_id=batch.dataset_id,
        variables=list(batch.variables),
        minimum_latitude=la0,
        maximum_latitude=la1,
        minimum_longitude=lo0,
        maximum_longitude=lo1,
        start_datetime=f"{batch.date_start.isoformat()}T00:00:00",
        end_datetime=f"{batch.date_end.isoformat()}T23:59:59",
        output_filename=str(out_file),
    )
    version = ""
    try:
        import xarray as xr

        with xr.open_dataset(out_file) as ds:
            version = str(ds.attrs.get("product_version") or ds.attrs.get("version") or "")
    except Exception:
        version = ""
    append_pull_log(
        build_pull_record(
            dataset_id=batch.dataset_id,
            date_start=batch.date_start.isoformat(),
            date_end=batch.date_end.isoformat(),
            variables=batch.variables,
            bbox=batch.bbox,
            dataset_version=version or None,
            file_sha256=_sha256_file(out_file),
        ),
        log_path=log_path,
    )
    return out_file


def load_events_parquet(path: Path | None = None) -> pd.DataFrame:
    path = path or DEFAULT_EVENTS_PATH
    return normalize_cufes_events_for_physics(pd.read_parquet(path))


def glorys_store_from_synthetic_days(
    days: Iterable[dt.date],
    *,
    config: dict[str, Any] | None = None,
    wcofs_h_m: np.ndarray | None = None,
    has_source: np.ndarray | None = None,
    wet_fraction: np.ndarray | None = None,
    lat: np.ndarray | None = None,
    lon: np.ndarray | None = None,
    roms_hmin_m: float | None = None,
    hmin_source: str = "wet_cell_minimum_h",
    wind_source_id: str = "ccmp_winds",
) -> GlorysFieldStore:
    cfg = config or load_overlap_config()
    min_wet = coarsen_min_wet_fraction(cfg)
    if lat is None or lon is None:
        bbox = cfg["pilot_bbox"]
        lat, lon = glorys_pilot_depth_grid(bbox)
    nj, ni = lat.size, lon.size
    if wcofs_h_m is None:
        wcofs_h_m = np.full((nj, ni), 500.0)
    if has_source is None:
        has_source = np.ones((nj, ni), dtype=bool)
    if roms_hmin_m is None:
        wet_vals = wcofs_h_m[has_source]
        finite = wet_vals[np.isfinite(wet_vals) & (wet_vals > 0)]
        roms_hmin_m = float(np.min(finite)) if finite.size else float("nan")
    if wet_fraction is None:
        wet_fraction = np.ones((nj, ni), dtype=float)
    store = GlorysFieldStore(
        wcofs_h_m=wcofs_h_m,
        has_source=has_source,
        wet_fraction=wet_fraction,
        min_wet_fraction=min_wet,
        roms_hmin_m=float(roms_hmin_m),
        hmin_source=hmin_source,
        lat=lat,
        lon=lon,
        wind_source_id=wind_source_id,
    )
    for day in days:
        store.days[day] = build_synthetic_day_fields(day, lat, lon)
    return store


def run_build_cufes_training_covariates(
    *,
    events_path: Path | None = None,
    output_path: Path | None = None,
    dry_run: bool = False,
    subset_fn: Callable[[GlorysSubsetBatch, Path], Path] | None = None,
    max_concurrent: int = 2,
) -> dict[str, Any]:
    """
    Load QC-kept CUFES events, plan GLORYS subsets, build training covariates table.

    Live Copernicus downloads are never run in CI; inject ``subset_fn`` or use ``dry_run``.
    """
    require_approved("glorys", purpose="training")
    events = load_events_parquet(events_path)
    days = unique_event_days(events)
    batches = plan_glorys_subset_batches(days)
    result: dict[str, Any] = {
        "input_event_count": int(len(events)),
        "unique_days": len(days),
        "subset_batch_count": len(batches),
        "batches": [
            {
                "dataset_id": b.dataset_id,
                "date_start": b.date_start.isoformat(),
                "date_end": b.date_end.isoformat(),
                "variables": list(b.variables),
            }
            for b in batches
        ],
    }
    if dry_run:
        return result

    if subset_fn is None:
        cfg_logs = load_overlap_config()
        log_path = REPO_ROOT / str(cfg_logs["pull_logs"]["glorys"])

        def subset_fn(batch: GlorysSubsetBatch, cache_dir: Path) -> Path:
            return _subset_batch_live(batch, cache_dir, log_path=log_path)

    cfg = load_overlap_config()
    lat, lon = glorys_pilot_depth_grid(cfg["pilot_bbox"])
    nj, ni = lat.size, lon.size
    store = glorys_store_from_synthetic_days(
        [],
        config=cfg,
        lat=lat,
        lon=lon,
        wcofs_h_m=np.full((nj, ni), 500.0),
    )
    cache_dir = REPO_ROOT / "data" / "cache" / "glorys_cufes"

    with ThreadPoolExecutor(max_workers=max_concurrent) as pool:
        futures = {
            pool.submit(subset_fn, batch, cache_dir): batch for batch in batches
        }
        for fut in as_completed(futures):
            fut.result()

    for day in days:
        store.days[day] = build_synthetic_day_fields(day, lat, lon)

    out_path = output_path or DEFAULT_OUTPUT_PATH
    drops_path = out_path.parent / DEFAULT_DROPS_NAME
    summary_path = out_path.parent / DEFAULT_DROP_SUMMARY_NAME
    table, qc, _drops, floor_qc = build_cufes_training_covariates_table(
        events,
        store,
        provenance=str(events_path or DEFAULT_EVENTS_PATH),
        drops_parquet_path=drops_path,
        drop_summary_json_path=summary_path,
    )
    write_training_covariates_parquet(
        table,
        out_path,
        entry=require_approved("glorys", purpose="training"),
        config=cfg,
        store=store,
    )
    result["output_path"] = str(out_path)
    result["qc"] = qc
    result["bottom_depth_qc"] = floor_qc
    return result
