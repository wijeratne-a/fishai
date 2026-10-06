"""Build adult CPS training table: observations × GLORYS (mirrors CUFES covariate join)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from fishai.ingestion.adult.constants import (
    ADULT_MIN_LENGTH_MM,
    DEFAULT_BUILD_SUMMARY_PATH,
    DEFAULT_DROP_SUMMARY_PATH,
    DEFAULT_DROPS_PATH,
    DEFAULT_EVENTS_PATH,
    DEFAULT_PROCESSED_DIR,
    DEFAULT_TRAINING_TABLE_PATH,
    NEARSHORE_CATCH_PATH,
    NEARSHORE_SETS_PATH,
    NEARSHORE_SPECIMENS_PATH,
    TRAINING_TABLE_EXTRA_COLUMNS,
    TRAWL_CATCH_PATH,
    TRAWL_HAULS_PATH,
    TRAWL_SPECIMENS_PATH,
)
from fishai.ingestion.adult.events import (
    filter_events_to_pilot_bbox,
    merge_adult_physics_events,
    nearshore_sets_to_physics_events,
    trawl_hauls_to_physics_events,
)
from fishai.ingestion.adult.observations import (
    append_implied_absence_observations,
    build_nearshore_observations,
    build_trawl_observations,
    observations_for_training_events,
)
from fishai.ingestion.adult.specimens import (
    median_length_by_event_species,
    normalize_nearshore_specimens,
    normalize_trawl_specimens,
)
from fishai.ingestion.physics.covariates import COL_EVENT_ID
from fishai.ingestion.physics.cufes_training_covariates import (
    TRAINING_OUTPUT_COLUMNS,
    GlorysFieldStore,
    build_cufes_training_covariates_table,
    write_training_covariates_parquet,
)
from fishai.ingestion.sources import load_sources_manifest, require_approved


def _pilot_bbox() -> tuple[float, float, float, float]:
    manifest = load_sources_manifest()
    pilot = manifest.get("pilot") or {}
    box = pilot.get("bbox") or {}
    return (
        float(box["lat_min"]),
        float(box["lat_max"]),
        float(box["lon_min"]),
        float(box["lon_max"]),
    )


def _read_parquet(path: Path) -> pd.DataFrame:
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_parquet(path)


def load_specimen_medians(
    *,
    trawl_specimens_path: Path | None = None,
    nearshore_specimens_path: Path | None = None,
) -> pd.Series:
    trawl_path = trawl_specimens_path or TRAWL_SPECIMENS_PATH
    near_path = nearshore_specimens_path or NEARSHORE_SPECIMENS_PATH
    trawl_df = _read_parquet(trawl_path)
    near_df = _read_parquet(near_path)
    if trawl_df.empty and near_df.empty:
        return pd.Series(dtype=float)
    if not trawl_df.empty and "event_id" not in trawl_df.columns:
        trawl_df = normalize_trawl_specimens(trawl_df.to_dict(orient="records"))
    if not near_df.empty and "event_id" not in near_df.columns:
        near_df = normalize_nearshore_specimens(near_df.to_dict(orient="records"))
    combined = pd.concat([trawl_df, near_df], ignore_index=True)
    return median_length_by_event_species(combined)


def assemble_adult_observations(
    *,
    trawl_catch_path: Path | None = None,
    nearshore_catch_path: Path | None = None,
    trawl_specimens_path: Path | None = None,
    nearshore_specimens_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    medians = load_specimen_medians(
        trawl_specimens_path=trawl_specimens_path,
        nearshore_specimens_path=nearshore_specimens_path,
    )
    trawl_catch = _read_parquet(trawl_catch_path or TRAWL_CATCH_PATH)
    near_catch = _read_parquet(nearshore_catch_path or NEARSHORE_CATCH_PATH)
    trawl_obs, trawl_stats = build_trawl_observations(trawl_catch, medians=medians)
    near_obs, near_stats = build_nearshore_observations(near_catch, medians=medians)
    obs = pd.concat([trawl_obs, near_obs], ignore_index=True)
    obs, implied_stats = append_implied_absence_observations(
        obs,
        trawl_catch=trawl_catch,
        nearshore_catch=near_catch,
    )
    summary = {
        "trawl_catch": trawl_stats,
        "nearshore_catch": near_stats,
        "implied_absences": implied_stats,
        "observation_rows_total": int(len(obs)),
        "presence_only_excluded_total": int(
            trawl_stats["presence_only_excluded"]
        ),
        "adult_min_length_mm": dict(ADULT_MIN_LENGTH_MM),
    }
    return obs, summary


def assemble_adult_physics_events(
    *,
    trawl_hauls_path: Path | None = None,
    nearshore_sets_path: Path | None = None,
    observation_event_ids: set[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    hauls = _read_parquet(trawl_hauls_path or TRAWL_HAULS_PATH)
    sets = _read_parquet(nearshore_sets_path or NEARSHORE_SETS_PATH)
    trawl_events = trawl_hauls_to_physics_events(hauls)
    near_events = nearshore_sets_to_physics_events(sets)
    merged = merge_adult_physics_events(trawl_events, near_events)
    lat_min, lat_max, lon_min, lon_max = _pilot_bbox()
    kept, bbox_drops = filter_events_to_pilot_bbox(
        merged,
        lat_min=lat_min,
        lat_max=lat_max,
        lon_min=lon_min,
        lon_max=lon_max,
    )
    if observation_event_ids is not None:
        kept = kept[kept[COL_EVENT_ID].astype(str).isin(observation_event_ids)].reset_index(
            drop=True
        )
    return kept, bbox_drops


def build_adult_cps_training_table(
    events: pd.DataFrame,
    observations: pd.DataFrame,
    store: GlorysFieldStore,
    *,
    provenance: str = "",
    drops_parquet_path: Path | None = None,
    drop_summary_json_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    """Join GLORYS covariates to adult events and attach species-level labels."""
    cov_table, qc, drops, floor_qc = build_cufes_training_covariates_table(
        events,
        store,
        provenance=provenance,
        drops_parquet_path=drops_parquet_path,
        drop_summary_json_path=drop_summary_json_path,
    )
    obs = observations_for_training_events(
        observations,
        set(events[COL_EVENT_ID].astype(str)),
    )
    if obs.empty:
        out = cov_table.copy()
        for col in TRAINING_TABLE_EXTRA_COLUMNS:
            out[col] = pd.NA
        return out, {**qc, "floor_qc": floor_qc, "observation_rows": 0}, drops

    merged = obs.merge(cov_table, on=COL_EVENT_ID, how="left", validate="many_to_one")
    merged["biology_excluded"] = merged["biology_excluded"].fillna(False)
    merged["biology_excluded_reason"] = merged["biology_excluded_reason"].fillna("")
    merged["excluded"] = merged["excluded"] | merged["biology_excluded"]
    for col in TRAINING_OUTPUT_COLUMNS:
        if col in merged.columns and col != COL_EVENT_ID:
            merged.loc[merged["excluded"], col] = pd.NA

    effort = events[
        [
            COL_EVENT_ID,
            "observation_source",
            "effort_duration_min",
        ]
        + ([c for c in ("effort_duration_null_reason",) if c in events.columns])
    ].drop_duplicates(subset=[COL_EVENT_ID])
    merged = merged.drop(columns=[c for c in ("observation_source",) if c in merged.columns])
    merged = merged.merge(effort, on=COL_EVENT_ID, how="left", suffixes=("", "_event"))

    column_order = list(TRAINING_OUTPUT_COLUMNS) + [
        c for c in TRAINING_TABLE_EXTRA_COLUMNS if c not in TRAINING_OUTPUT_COLUMNS
    ]
    for col in column_order:
        if col not in merged.columns:
            merged[col] = pd.NA
    out = merged[column_order]
    qc_out = {**qc, "floor_qc": floor_qc, "observation_rows": int(len(out))}
    return out, qc_out, drops


def run_build_adult_cps_training_table(
    *,
    trawl_hauls_path: Path | None = None,
    trawl_catch_path: Path | None = None,
    trawl_specimens_path: Path | None = None,
    nearshore_sets_path: Path | None = None,
    nearshore_catch_path: Path | None = None,
    nearshore_specimens_path: Path | None = None,
    events_path: Path | None = None,
    output_path: Path | None = None,
    store: GlorysFieldStore | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Load processed CPS tables, apply adult/species QC, join GLORYS covariates.

    ``dry_run`` skips Copernicus I/O and returns row-count summary only.
    """
    require_approved("glorys", purpose="training")
    observations, obs_summary = assemble_adult_observations(
        trawl_catch_path=trawl_catch_path,
        nearshore_catch_path=nearshore_catch_path,
        trawl_specimens_path=trawl_specimens_path,
        nearshore_specimens_path=nearshore_specimens_path,
    )
    event_ids = set(observations["event_id"].astype(str)) if not observations.empty else set()
    events, bbox_drops = assemble_adult_physics_events(
        trawl_hauls_path=trawl_hauls_path,
        nearshore_sets_path=nearshore_sets_path,
        observation_event_ids=event_ids,
    )
    out_events = events_path or DEFAULT_EVENTS_PATH
    out_table = output_path or DEFAULT_TRAINING_TABLE_PATH
    result: dict[str, Any] = {
        "observation_summary": obs_summary,
        "physics_event_count": int(len(events)),
        "pilot_bbox_dropped_events": int(len(bbox_drops)),
        "events_path": str(out_events),
        "output_path": str(out_table),
        "dry_run": dry_run,
    }
    if dry_run:
        result["observation_rows_by_source"] = (
            observations.groupby("observation_source").size().astype(int).to_dict()
            if not observations.empty
            else {}
        )
        if not observations.empty:
            result["encounter_counts"] = (
                observations.groupby(["species", "observation_source", "encounter"])
                .size()
                .astype(int)
                .to_dict()
            )
        return result

    out_events.parent.mkdir(parents=True, exist_ok=True)
    events.to_parquet(out_events, index=False)

    if store is None:
        obs_kept = observations_for_training_events(
            observations,
            set(events[COL_EVENT_ID].astype(str)),
        )
        out_table.parent.mkdir(parents=True, exist_ok=True)
        obs_kept.to_parquet(out_table, index=False)
        result["glorys_join"] = "blocked_no_store"
        result["observation_rows_written"] = int(len(obs_kept))
        result["encounter_counts"] = (
            obs_kept.groupby(["species", "observation_source", "encounter"])
            .size()
            .astype(int)
            .to_dict()
            if not obs_kept.empty
            else {}
        )
        summary_file = out_table.parent / DEFAULT_BUILD_SUMMARY_PATH.name
        summary_file.write_text(json.dumps({**result}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["build_summary_path"] = str(summary_file)
        return result

    drops_path = out_table.parent / DEFAULT_DROPS_PATH.name
    summary_path = out_table.parent / DEFAULT_DROP_SUMMARY_PATH.name
    table, qc, _drops = build_adult_cps_training_table(
        events,
        observations,
        store,
        provenance=str(out_events),
        drops_parquet_path=drops_path,
        drop_summary_json_path=summary_path,
    )
    write_training_covariates_parquet(
        table,
        out_table,
        entry=require_approved("glorys", purpose="training"),
        store=store,
    )
    build_summary = {
        **result,
        "qc": qc,
        "observation_rows_by_source": (
            table.groupby("observation_source").size().astype(int).to_dict()
            if not table.empty
            else {}
        ),
        "training_rows_kept": int((~table["excluded"]).sum()) if not table.empty else 0,
        "training_rows_excluded": int(table["excluded"].sum()) if not table.empty else 0,
    }
    summary_file = out_table.parent / DEFAULT_BUILD_SUMMARY_PATH.name
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_text(json.dumps(build_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["build_summary_path"] = str(summary_file)
    result["drops_path"] = str(drops_path)
    result["qc"] = qc
    return result


def processed_output_dir() -> Path:
    return DEFAULT_PROCESSED_DIR
