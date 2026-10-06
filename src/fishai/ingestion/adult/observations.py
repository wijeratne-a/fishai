"""Adult observation rows from trawl and nearshore catch (presence-only excluded)."""

from __future__ import annotations

from typing import Any

import pandas as pd

from fishai.ingestion.adult.constants import (
    ADULT_MIN_LENGTH_MM,
    EXCLUDE_REASON_JUVENILE,
    EXCLUDE_REASON_NO_SPECIMEN,
    EXCLUDE_REASON_PRESENCE_ONLY,
    OBSERVATION_SOURCE_NEARSHORE,
    OBSERVATION_SOURCE_TRAWL,
    PILOT_SPECIES,
)
from fishai.ingestion.adult.specimens import median_length_by_event_species


def _encounter_from_measurements(
    *,
    weight_kg: float | None,
    count: int | None,
) -> int:
    if weight_kg is not None and weight_kg > 0:
        return 1
    if count is not None and count > 0:
        return 1
    return 0


def _adult_gate(
    event_id: str,
    species: str,
    medians: pd.Series,
) -> tuple[bool, str | None, float | None]:
    key = (event_id, species)
    if key not in medians.index:
        return False, EXCLUDE_REASON_NO_SPECIMEN, None
    median_len = float(medians.loc[key])
    cutoff = ADULT_MIN_LENGTH_MM.get(species)
    if cutoff is None:
        return False, EXCLUDE_REASON_NO_SPECIMEN, median_len
    if median_len < cutoff:
        return False, EXCLUDE_REASON_JUVENILE, median_len
    return True, None, median_len


def build_trawl_observations(
    catch: pd.DataFrame,
    *,
    medians: pd.Series,
) -> tuple[pd.DataFrame, dict[str, int]]:
    stats = {
        "input_rows": 0,
        "presence_only_excluded": 0,
        "non_pilot_species_skipped": 0,
        "juvenile_excluded": 0,
        "no_specimen_excluded": 0,
        "rows_kept": 0,
    }
    rows: list[dict[str, Any]] = []
    if catch.empty:
        return pd.DataFrame(), stats
    for _, row in catch.iterrows():
        stats["input_rows"] += 1
        if bool(row.get("presence_only")):
            stats["presence_only_excluded"] += 1
            continue
        species = str(row.get("species") or "").strip()
        if species not in PILOT_SPECIES:
            stats["non_pilot_species_skipped"] += 1
            continue
        event_id = str(row["haul_id"])
        adult_ok, reason, median_len = _adult_gate(event_id, species, medians)
        if not adult_ok:
            if reason == EXCLUDE_REASON_JUVENILE:
                stats["juvenile_excluded"] += 1
            else:
                stats["no_specimen_excluded"] += 1
            continue
        weight = row.get("weight_kg")
        weight_f = float(weight) if weight is not None and pd.notna(weight) else None
        count_raw = row.get("count_raised_est")
        if count_raw is None or pd.isna(count_raw):
            count_raw = row.get("subsample_count")
        count = int(count_raw) if count_raw is not None and pd.notna(count_raw) else None
        rows.append(
            {
                "event_id": event_id,
                "species": species,
                "observation_source": OBSERVATION_SOURCE_TRAWL,
                "encounter": _encounter_from_measurements(weight_kg=weight_f, count=count),
                "weight_kg": weight_f,
                "count_observed": count,
                "adult_median_length_mm": median_len,
                "biology_excluded": False,
                "biology_excluded_reason": "",
            }
        )
        stats["rows_kept"] += 1
    return pd.DataFrame(rows), stats


def build_nearshore_observations(
    catch: pd.DataFrame,
    *,
    medians: pd.Series,
) -> tuple[pd.DataFrame, dict[str, int]]:
    stats = {
        "input_rows": 0,
        "presence_only_excluded": 0,
        "non_pilot_species_skipped": 0,
        "juvenile_excluded": 0,
        "no_specimen_excluded": 0,
        "rows_kept": 0,
    }
    rows: list[dict[str, Any]] = []
    if catch.empty:
        return pd.DataFrame(), stats
    for _, row in catch.iterrows():
        stats["input_rows"] += 1
        species = str(row.get("scientific_name") or row.get("species") or "").strip()
        if species not in PILOT_SPECIES:
            stats["non_pilot_species_skipped"] += 1
            continue
        event_id = str(row["set_id"])
        adult_ok, reason, median_len = _adult_gate(event_id, species, medians)
        if not adult_ok:
            if reason == EXCLUDE_REASON_JUVENILE:
                stats["juvenile_excluded"] += 1
            else:
                stats["no_specimen_excluded"] += 1
            continue
        weight = row.get("total_weight_kg")
        weight_f = float(weight) if weight is not None and pd.notna(weight) else None
        count_raw = row.get("total_number")
        count = int(count_raw) if count_raw is not None and pd.notna(count_raw) else None
        rows.append(
            {
                "event_id": event_id,
                "species": species,
                "observation_source": OBSERVATION_SOURCE_NEARSHORE,
                "encounter": _encounter_from_measurements(weight_kg=weight_f, count=count),
                "weight_kg": weight_f,
                "count_observed": count,
                "adult_median_length_mm": median_len,
                "biology_excluded": False,
                "biology_excluded_reason": "",
            }
        )
        stats["rows_kept"] += 1
    return pd.DataFrame(rows), stats


def observations_for_training_events(
    observations: pd.DataFrame,
    event_ids: set[str],
) -> pd.DataFrame:
    if observations.empty:
        return observations
    return observations[observations["event_id"].astype(str).isin(event_ids)].reset_index(drop=True)
