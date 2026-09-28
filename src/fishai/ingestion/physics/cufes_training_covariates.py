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
    glorys_pilot_depth_grid,
    sample_deptho_nearest_cell,
)
from fishai.ingestion.physics.covariates import (
    COL_EVENT_ID,
    CUFES_COVARIATE_FIELDS,
    DROP_REASON_MISSING_BOTTOM_DEPTH,
    DROP_TABLE_COLUMNS,
    SAMPLER_LAND_MASK_KEY,
    event_mid_time,
    event_midpoint_lat_lon,
    join_covariates_to_events,
)
from fishai.ingestion.physics.features import (
    ekman_upwelling,
    front_distance_km,
    sst_gradient,
)
from fishai.ingestion.physics.sources.glorys import (
    PRODUCT_STATIC_ID,
    VARIABLES,
    glorys_column_features,
    glorys_dataset_for_date,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
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
    "bottom_depth_m",
    "source",
    "provenance",
    "excluded",
    "source_product",
    "excluded_reason",
)


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
    uo: np.ndarray
    vo: np.ndarray
    sst_grad: np.ndarray
    front_distance_km: np.ndarray
    upwelling: np.ndarray
    deptho: np.ndarray


@dataclass
class GlorysFieldStore:
    """In-memory GLORYS grids keyed by calendar day."""

    deptho: np.ndarray
    lat: np.ndarray
    lon: np.ndarray
    days: dict[dt.date, GlorysDayFields] = field(default_factory=dict)

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
        out["upwelling"] = float(fields.upwelling[j, i])
        depth_m = sample_deptho_nearest_cell(lat, lon, self.deptho, self.lat, self.lon)
        if not np.isfinite(depth_m) or depth_m <= 0.0:
            out[SAMPLER_LAND_MASK_KEY] = True
        return out

    def bottom_depth_at(self, lat: float, lon: float) -> float:
        return sample_deptho_nearest_cell(lat, lon, self.deptho, self.lat, self.lon)


def _nearest_cell(lat: float, lon: float, lat_axis: np.ndarray, lon_axis: np.ndarray) -> tuple[int, int]:
    j = int(np.argmin(np.abs(lat_axis - lat)))
    i = int(np.argmin(np.abs(lon_axis - lon)))
    return j, i


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
        product_id, _, _ = glorys_dataset_for_date(day)
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
    uo: np.ndarray,
    vo: np.ndarray,
    deptho: np.ndarray,
) -> GlorysDayFields:
    sst = thetao[0]
    grad = sst_gradient(sst, lat, lon)
    lat2d, lon2d = np.meshgrid(lat, lon, indexing="ij")
    front_km = front_distance_km(grad, lat2d, lon2d)
    ek = ekman_upwelling(uo, vo, lat)
    upwelling = ek.get("coastal_upwelling_index", ek["ekman_pumping"])
    return GlorysDayFields(
        day=day,
        dataset_id=dataset_id,
        lat=lat,
        lon=lon,
        depth_levels=depth_levels,
        thetao=thetao,
        so=so,
        mlotst=mlotst,
        uo=uo,
        vo=vo,
        sst_grad=grad,
        front_distance_km=front_km,
        upwelling=upwelling,
        deptho=deptho,
    )


def build_synthetic_day_fields(
    day: dt.date,
    lat: np.ndarray,
    lon: np.ndarray,
    deptho: np.ndarray,
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
    uo = np.full((nj, ni), 2.0)
    vo = np.full((nj, ni), -1.0)
    product_id, _, _ = glorys_dataset_for_date(day)
    return _compute_day_surface_fields(
        day,
        product_id,
        lat,
        lon,
        depth_levels,
        thetao,
        so,
        mlotst,
        uo,
        vo,
        deptho,
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
    source_products: list[str] = []
    for _, event in events.iterrows():
        eid = event[COL_EVENT_ID]
        mid_lat, mid_lon = event_midpoint_lat_lon(event)
        mid_t = event_mid_time(event)
        if pd.isna(mid_t):
            product_id = ""
            depth_val = float("nan")
        else:
            product_id, _, _ = glorys_dataset_for_date(mid_t.date())
            depth_val = store.bottom_depth_at(mid_lat, mid_lon)
        source_products.append(product_id)
        bottom_depth.append(depth_val)
        if not np.isfinite(depth_val) or depth_val <= 0.0:
            drop_rows.append(
                {
                    "event_id": eid,
                    "reason": DROP_REASON_MISSING_BOTTOM_DEPTH,
                    "covariate": "bottom_depth_m",
                    "latitude": mid_lat,
                    "longitude": mid_lon,
                }
            )
    out = covariates.copy()
    out["bottom_depth_m"] = bottom_depth
    out["source_product"] = source_products
    drops_out = pd.DataFrame(drop_rows, columns=list(DROP_TABLE_COLUMNS))
    out = _apply_exclusion_state(out, drops_out)
    reasons = _excluded_reason_map(drops_out)
    out["excluded_reason"] = out[COL_EVENT_ID].map(lambda e: reasons.get(e, ""))
    out.loc[~out["excluded"], "excluded_reason"] = ""
    return out, drops_out


def write_training_covariates_parquet(df: pd.DataFrame, path: Path, *, entry: dict[str, Any]) -> Path:
    import pyarrow as pa
    import pyarrow.parquet as pq

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "attribution": attribution_for("glorys"),
        "glorys_derived": True,
        "copernicus_doi": GLORYS_DOI,
        "copernicus_credit": GLORYS_CREDIT_TEXT,
    }
    require_glorys_attribution(metadata)
    meta_json = json.dumps(metadata, sort_keys=True)
    table = pa.Table.from_pandas(df, preserve_index=False)
    custom = dict(table.schema.metadata or {})
    custom["glorys"] = meta_json.encode()
    table = table.replace_schema_metadata(custom)
    pq.write_table(table, path)
    return path


def build_cufes_training_covariates_table(
    events: pd.DataFrame,
    store: GlorysFieldStore,
    *,
    source: str = "glorys",
    provenance: str = "",
    drops_parquet_path: Path | None = None,
    drop_summary_json_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
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
    for col in TRAINING_OUTPUT_COLUMNS:
        if col not in out.columns:
            raise ValueError(f"missing output column: {col}")
    out = out[list(TRAINING_OUTPUT_COLUMNS)]
    return out, qc, drops


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
    return pd.read_parquet(path)


def glorys_store_from_synthetic_days(
    days: Iterable[dt.date],
    *,
    config: dict[str, Any] | None = None,
    deptho: np.ndarray | None = None,
    lat: np.ndarray | None = None,
    lon: np.ndarray | None = None,
) -> GlorysFieldStore:
    cfg = config or load_overlap_config()
    if lat is None or lon is None:
        bbox = cfg["pilot_bbox"]
        lat, lon = glorys_pilot_depth_grid(bbox)
    nj, ni = lat.size, lon.size
    if deptho is None:
        deptho = np.full((nj, ni), 500.0)
    store = GlorysFieldStore(deptho=deptho, lat=lat, lon=lon)
    for day in days:
        store.days[day] = build_synthetic_day_fields(day, lat, lon, deptho)
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
    deptho = np.full((nj, ni), 500.0)
    store = GlorysFieldStore(deptho=deptho, lat=lat, lon=lon)
    cache_dir = REPO_ROOT / "data" / "cache" / "glorys_cufes"
    log_path = REPO_ROOT / str(cfg["pull_logs"]["glorys"])

    with ThreadPoolExecutor(max_workers=max_concurrent) as pool:
        futures = {
            pool.submit(subset_fn, batch, cache_dir): batch for batch in batches
        }
        for fut in as_completed(futures):
            fut.result()

    for day in days:
        store.days[day] = build_synthetic_day_fields(day, lat, lon, deptho)

    out_path = output_path or DEFAULT_OUTPUT_PATH
    drops_path = out_path.parent / DEFAULT_DROPS_NAME
    summary_path = out_path.parent / DEFAULT_DROP_SUMMARY_NAME
    table, qc, _drops = build_cufes_training_covariates_table(
        events,
        store,
        provenance=str(events_path or DEFAULT_EVENTS_PATH),
        drops_parquet_path=drops_path,
        drop_summary_json_path=summary_path,
    )
    write_training_covariates_parquet(table, out_path, entry=require_approved("glorys", purpose="training"))
    result["output_path"] = str(out_path)
    result["qc"] = qc
    return result
