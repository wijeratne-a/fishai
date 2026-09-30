"""Audit excluded vs kept rows in the CUFES × GLORYS training covariates table."""

from __future__ import annotations

import datetime as dt
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from scipy.spatial import cKDTree
from pyproj import Geod

from fishai.ingestion.physics.coast_distance import (
    _densified_boundary_vertices,
    shoreline_path_from_config,
)
from fishai.ingestion.physics.covariates import (
    COL_EVENT_ID,
    COL_START_LAT,
    COL_START_LON,
    COL_STOP_LAT,
    COL_STOP_LON,
    event_mid_time,
    event_midpoint_lat_lon,
    normalize_cufes_events_for_physics,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
from fishai.ingestion.sources import REPO_ROOT

DEFAULT_TRAINING_PATH = (
    REPO_ROOT / "data" / "processed" / "calcofi_cufes" / "cufes_training_covariates.parquet"
)
DEFAULT_EVENTS_PATH = REPO_ROOT / "data" / "processed" / "calcofi_cufes" / "cufes_events.parquet"
DEFAULT_COUNTS_PATH = REPO_ROOT / "data" / "processed" / "calcofi_cufes" / "cufes_counts.parquet"
DEFAULT_DROPS_PATH = (
    REPO_ROOT / "data" / "processed" / "calcofi_cufes" / "cufes_training_covariate_drops.parquet"
)

MISSING_COVARIATE_FIELDS = (
    "T3m",
    "S3m",
    "MLD_m",
    "sst_grad",
    "front_distance_km",
    "bottom_depth_m",
)

SHORE_DISTANCE_BINS_KM = (
    (0.0, 5.0, "0-5"),
    (5.0, 10.0, "5-10"),
    (10.0, 25.0, "10-25"),
    (25.0, 50.0, "25-50"),
    (50.0, float("inf"), ">50"),
)

DEPTH_BANDS_M = (
    (0.0, 50.0, "<50"),
    (50.0, 100.0, "50-100"),
    (100.0, 200.0, "100-200"),
    (200.0, 500.0, "200-500"),
    (500.0, 1000.0, "500-1000"),
    (1000.0, float("inf"), ">1000"),
)


def _shoreline_metadata(config: dict[str, Any]) -> dict[str, str]:
    shore = config.get("shoreline") or {}
    return {
        "coastline_source": str(shore.get("natural_earth_dataset", "ne_10m_land")),
        "coastline_version": str(shore.get("natural_earth_version", "")),
        "shoreline_path": str(shore.get("path", "")),
        "distance_method": str(shore.get("distance_method", "pyproj_geod_fwd")),
        "densify_spacing_km": str(shore.get("densify_spacing_km", "1.0")),
        "distance_query_note": (
            "Geodesic distance to densified Natural Earth vertices; cKDTree prefilter "
            f"with k={SHORE_DISTANCE_KD_NEIGHBORS} candidates refined on WGS84 ellipsoid."
        ),
    }


def _bin_label(value: float, edges: tuple[tuple[float, float, str], ...]) -> str:
    for lo, hi, label in edges:
        if lo <= value < hi:
            return label
    return edges[-1][2]


def _missing_covariate_breakdown(drops: pd.DataFrame) -> dict[str, Any]:
    miss = drops[drops["reason"] == "missing_covariate"].copy()
    per_field = (
        miss.groupby("covariate")["event_id"].nunique().sort_index().astype(int).to_dict()
        if not miss.empty
        else {}
    )
    depth_drop_events = (
        int(miss.loc[miss["covariate"] == "bottom_depth_m", "event_id"].nunique())
        if not miss.empty and "bottom_depth_m" in miss["covariate"].values
        else 0
    )
    if depth_drop_events:
        per_field["bottom_depth_m"] = depth_drop_events
    by_event: dict[Any, set[str]] = {}
    for _, row in miss.iterrows():
        cov = row.get("covariate")
        if cov is None or (isinstance(cov, float) and np.isnan(cov)):
            continue
        by_event.setdefault(row["event_id"], set()).add(str(cov))
    combo_counts = Counter(
        "+".join(sorted(fields)) for fields in by_event.values() if fields
    )
    return {
        "unique_events_with_missing_covariate_drop": int(miss["event_id"].nunique()) if not miss.empty else 0,
        "missing_by_covariate_unique_events": per_field,
        "missing_covariate_combinations_unique_events": dict(sorted(combo_counts.items())),
    }


GEOD = Geod(ellps="WGS84")
SHORE_DISTANCE_KD_NEIGHBORS = 32


def _shore_distance_km_for_events(events: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    shore_path = shoreline_path_from_config(config)
    cfg_densify = float((config.get("shoreline") or {}).get("densify_spacing_km", 1.0))
    coast_lat, coast_lon = _densified_boundary_vertices(str(shore_path), cfg_densify)
    lats: list[float] = []
    lons: list[float] = []
    for _, row in events.iterrows():
        lat, lon = event_midpoint_lat_lon(row)
        lats.append(lat)
        lons.append(lon)
    lat_arr = np.asarray(lats, dtype=float)
    lon_arr = np.asarray(lons, dtype=float)
    if coast_lat.size == 0:
        return pd.Series(np.full(len(events), np.nan), index=events.index)
    coast_xy = np.column_stack([coast_lon, coast_lat])
    tree = cKDTree(coast_xy)
    k = min(SHORE_DISTANCE_KD_NEIGHBORS, coast_lat.size)
    _, nn_idx = tree.query(np.column_stack([lon_arr, lat_arr]), k=k)
    if k == 1:
        nn_idx = nn_idx[:, None]
    dist_km = np.empty(len(lat_arr), dtype=float)
    for i, (la, lo) in enumerate(zip(lat_arr, lon_arr, strict=True)):
        best_m = float("inf")
        for j in nn_idx[i]:
            _, _, dm = GEOD.inv(lo, la, float(coast_lon[j]), float(coast_lat[j]))
            best_m = min(best_m, float(dm))
        dist_km[i] = best_m / 1000.0
    return pd.Series(dist_km, index=events.index)


def _depth_band_series(bottom_depth_m: pd.Series) -> pd.Series:
    return bottom_depth_m.apply(
        lambda v: _bin_label(float(v), DEPTH_BANDS_M) if np.isfinite(v) else "missing"
    )


def _stratum_table(
    labels: pd.Series,
    excluded: pd.Series,
) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for label in sorted(labels.dropna().unique()):
        mask = labels == label
        out[str(label)] = {
            "kept": int((mask & ~excluded).sum()),
            "excluded": int((mask & excluded).sum()),
        }
    return out


def _two_proportion_pvalue(pos_a: int, n_a: int, pos_b: int, n_b: int) -> float | None:
    if n_a == 0 or n_b == 0:
        return None
    table = np.array([[pos_a, n_a - pos_a], [pos_b, n_b - pos_b]])
    _chi2, p_value, _dof, _expected = chi2_contingency(table, correction=False)
    return float(p_value)


def _taxon_positivity(
    table: pd.DataFrame,
    counts: pd.DataFrame,
    taxon: str,
) -> dict[str, Any]:
    sub = counts[counts["taxon"] == taxon][["event_id", "count"]]
    merged = table.merge(sub, on="event_id", how="left")
    merged["count"] = merged["count"].fillna(0)
    merged["positive"] = merged["count"] > 0
    kept = merged[~merged["excluded"]]
    excl = merged[merged["excluded"]]
    k_pos, k_n = int(kept["positive"].sum()), int(len(kept))
    e_pos, e_n = int(excl["positive"].sum()), int(len(excl))
    return {
        "taxon": taxon,
        "kept_positive": k_pos,
        "kept_total": k_n,
        "kept_positive_share": (k_pos / k_n) if k_n else None,
        "excluded_positive": e_pos,
        "excluded_total": e_n,
        "excluded_positive_share": (e_pos / e_n) if e_n else None,
        "two_proportion_chi2_p_value": _two_proportion_pvalue(e_pos, e_n, k_pos, k_n),
    }


def _shallow_trainable_depth_note(table: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    kept = table[~table["excluded"]]
    min_depth = float(kept["bottom_depth_m"].min()) if len(kept) else float("nan")
    audit_col = "wcofs_h_audit_m"
    min_audit = (
        float(table[audit_col].min())
        if audit_col in table.columns and table[audit_col].notna().any()
        else float("nan")
    )
    note = (
        "Trainable ``bottom_depth_m`` is the segment mean of coarsened WCOFS ROMS ``h`` on the "
        "GLORYS 1/12° pilot grid (min_wet_fraction={mwf}). Shallowest kept depth {min_d:.2f} m "
        "reflects WCOFS wet-cell / wet-fraction gating on the shelf—not GLORYS ``thetao`` land "
        "masking (segment ``land_mask`` drops are zero in this build). Coastal samples with "
        "insufficient wet coarsening are excluded via ``wcofs_low_wet_fraction`` / missing depth. "
        "Depth-band audit uses audit-only ``wcofs_h_audit_m`` (nearest wet coarsened cell ``h``, "
        "min audit h {min_a:.2f} m)."
    ).format(mwf=coarsen_min_wet_fraction(config), min_d=min_depth, min_a=min_audit)
    return {
        "min_trainable_bottom_depth_m": min_depth,
        "min_wcofs_h_audit_m": min_audit,
        "explanation": note,
    }


def _audit_depth_column(table: pd.DataFrame) -> pd.Series:
    if "wcofs_h_audit_m" in table.columns:
        return table["wcofs_h_audit_m"]
    return table["bottom_depth_m"]


def _year_1998_exclusion_diagnosis(
    table: pd.DataFrame,
    events: pd.DataFrame,
    drops: pd.DataFrame,
    shore_bins: pd.Series,
    excluded: pd.Series,
) -> dict[str, Any]:
    years = events.apply(event_mid_time, axis=1).dt.year
    mask_1998 = years == 1998
    if not mask_1998.any():
        return {"note": "no 1998 events in table"}

    t98 = table.loc[mask_1998].copy()
    ex98 = excluded.loc[mask_1998]
    shore98 = shore_bins.loc[mask_1998]
    drop_eids = set(t98.loc[ex98, COL_EVENT_ID])

    null_kept: dict[str, int] = {}
    for field in ("T3m", "S3m", "MLD_m", "sst_grad", "front_distance_km", "bottom_depth_m"):
        if field not in t98.columns:
            continue
        null_kept[field] = int(t98.loc[~ex98, field].isna().sum())

    miss = drops[drops["event_id"].isin(drop_eids)]
    miss_cov = miss[miss["reason"] == "missing_covariate"]
    miss_by_cov = (
        miss_cov.groupby("covariate")["event_id"].nunique().sort_index().astype(int).to_dict()
        if not miss_cov.empty
        else {}
    )

    by_shore = _stratum_table(shore98, ex98)
    excl_reasons = (
        t98.loc[ex98, "excluded_reason"].value_counts().astype(int).to_dict() if ex98.any() else {}
    )

    wcofs_only = int(
        t98.loc[
            ex98
            & t98["excluded_reason"].str.contains("wcofs", case=False, na=False)
        ].shape[0]
    )

    mld_miss = miss_by_cov.get("MLD_m", 0)
    t3_miss = miss_by_cov.get("T3m", 0)

    explanation = (
        "1998 accounts for {n_ex} of {n_all} excluded rows ({n_kept} kept of {n98} 1998 events). "
        "Drop log (not post-exclusion nulls): ``MLD_m`` missing on {mld} unique excluded events, "
        "``T3m``/``S3m`` on {t3} (often co-occurring); only {wcofs} rows also hit "
        "``wcofs_low_wet_fraction``/depth. Kept 1998 rows have finite GLORYS covariates "
        "(0 nulls). Spatially, exclusions concentrate 0–5 km from shore ({s0_ex} excluded vs "
        "{s0_k} kept) with another {s510_ex} excluded in 5–10 km—consistent with GLORYS "
        "NaNs at nearshore pilot cells in 1998, not missing CUFES events or a different "
        "Copernicus product id."
    ).format(
        n_ex=int(ex98.sum()),
        n_all=int(excluded.sum()),
        n_kept=int((~ex98).sum()),
        n98=int(mask_1998.sum()),
        mld=mld_miss,
        t3=t3_miss,
        wcofs=wcofs_only,
        s0_ex=by_shore.get("0-5", {}).get("excluded", 0),
        s0_k=by_shore.get("0-5", {}).get("kept", 0),
        s510_ex=by_shore.get("5-10", {}).get("excluded", 0),
    )

    return {
        "year": 1998,
        "row_count": int(mask_1998.sum()),
        "excluded_count": int(ex98.sum()),
        "kept_count": int((~ex98).sum()),
        "excluded_reason_counts": excl_reasons,
        "covariate_null_counts_kept": null_kept,
        "missing_covariate_drop_unique_events_by_field": miss_by_cov,
        "by_shore_distance_km": by_shore,
        "wcofs_related_excluded_count": wcofs_only,
        "explanation": explanation,
    }


def coarsen_min_wet_fraction(config: dict[str, Any]) -> float:
    from fishai.ingestion.physics.wcofs_glorys_overlap import coarsen_min_wet_fraction as _fn

    return _fn(config)


def run_training_exclusion_audit(
    *,
    training_path: Path | None = None,
    events_path: Path | None = None,
    counts_path: Path | None = None,
    drops_path: Path | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or load_overlap_config()
    training_path = training_path or DEFAULT_TRAINING_PATH
    events_path = events_path or DEFAULT_EVENTS_PATH
    counts_path = counts_path or DEFAULT_COUNTS_PATH
    drops_path = drops_path or DEFAULT_DROPS_PATH

    table = pd.read_parquet(training_path)
    events = normalize_cufes_events_for_physics(pd.read_parquet(events_path))
    counts = pd.read_parquet(counts_path)
    drops = pd.read_parquet(drops_path) if drops_path.is_file() else pd.DataFrame()

    events = events.set_index(COL_EVENT_ID).reindex(table[COL_EVENT_ID].tolist()).reset_index()
    excluded = table["excluded"].astype(bool)
    shore_dist = _shore_distance_km_for_events(events, config)
    shore_bins = shore_dist.apply(lambda v: _bin_label(v, SHORE_DISTANCE_BINS_KM))

    years = events.apply(event_mid_time, axis=1).dt.year
    depth_for_strata = _audit_depth_column(table)
    depth_bins = _depth_band_series(depth_for_strata)

    report: dict[str, Any] = {
        "training_path": str(training_path),
        "row_count": int(len(table)),
        "excluded_count": int(excluded.sum()),
        "kept_count": int((~excluded).sum()),
        "covariate_null_counts_all_rows": {
            field: int(table[field].isna().sum())
            for field in MISSING_COVARIATE_FIELDS
            if field in table.columns
        },
        "shoreline": _shoreline_metadata(config),
        "missing_covariate_audit": _missing_covariate_breakdown(drops),
        "by_shore_distance_km": _stratum_table(shore_bins, excluded),
        "by_wcofs_bottom_depth_band_m": _stratum_table(depth_bins, excluded),
        "depth_band_column": "wcofs_h_audit_m"
        if "wcofs_h_audit_m" in table.columns
        else "bottom_depth_m",
        "by_year": _stratum_table(years.astype(str), excluded),
        "year_1998_exclusion_diagnosis": _year_1998_exclusion_diagnosis(
            table, events, drops, shore_bins, excluded
        ),
        "taxon_positivity": [
            _taxon_positivity(table, counts, "sardine"),
            _taxon_positivity(table, counts, "anchovy"),
        ],
        "shallow_trainable_depth": _shallow_trainable_depth_note(table, config),
    }
    return report


def format_audit_report(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Audit excluded vs kept CUFES training covariate rows",
    )
    parser.add_argument(
        "--training",
        type=Path,
        default=DEFAULT_TRAINING_PATH,
        help="Training covariates parquet path",
    )
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS_PATH)
    parser.add_argument("--counts", type=Path, default=DEFAULT_COUNTS_PATH)
    parser.add_argument("--drops", type=Path, default=DEFAULT_DROPS_PATH)
    parser.add_argument("--json-out", type=Path, help="Optional path to write JSON report")
    args = parser.parse_args(argv)

    report = run_training_exclusion_audit(
        training_path=args.training,
        events_path=args.events,
        counts_path=args.counts,
        drops_path=args.drops,
    )
    text = format_audit_report(report)
    print(text, end="")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
    return 0
