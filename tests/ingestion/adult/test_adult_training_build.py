"""Adult CPS training table (synthetic fixtures only)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import pytest

from fishai.ingestion.adult.constants import (
    ADULT_MIN_LENGTH_MM,
    OBSERVATION_SOURCE_NEARSHORE,
    OBSERVATION_SOURCE_TRAWL,
)
from fishai.ingestion.adult.observations import (
    append_implied_absence_observations,
    build_nearshore_observations,
    build_trawl_observations,
)
from fishai.ingestion.adult.specimens import median_length_by_event_species
from fishai.ingestion.adult.training_build import (
    assemble_adult_observations,
    build_adult_cps_training_table,
)
from fishai.ingestion.adult.events import (
    nearshore_sets_to_physics_events,
    trawl_hauls_to_physics_events,
)
from fishai.ingestion.physics.covariates import (
    COL_EVENT_ID,
    DROP_REASON_TOO_FEW_TRACK_POINTS,
    mean_covariates_along_segment,
)
from tests.ingestion.physics.cufes_glorys_synthetic_fixture import glorys_store_from_synthetic_days


GLORYS_TEST_DAY = dt.date(2021, 7, 1)


def _synthetic_trawl_haul() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "haul_id": "CPSTrawl:209901:SY:1",
                "time": "2021-07-01T12:00:00+00:00",
                "haulback_time": "2021-07-01T12:30:00+00:00",
                "lat": 33.5,
                "lon": -120.0,
                "stop_lat": 33.52,
                "stop_lon": -119.98,
                "tow_duration_min": 30.0,
            }
        ]
    )


def _synthetic_nearshore_set() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "set_id": "CPSNearshore:209901:SY:1",
                "time_utc": "2021-07-01T14:00:00+00:00",
                "latitude": 33.6,
                "longitude": -119.5,
                "effort_duration_min": None,
                "effort_duration_null_reason": "not_applicable_purse_seine_set",
            }
        ]
    )


def test_presence_only_trawl_rows_never_enter_observations() -> None:
    medians = median_length_by_event_species(
        pd.DataFrame(
            [
                {
                    "event_id": "CPSTrawl:209901:SY:1",
                    "species": "Sardinops sagax",
                    "length_mm": 150.0,
                }
            ]
        )
    )
    catch = pd.DataFrame(
        [
            {
                "haul_id": "CPSTrawl:209901:SY:1",
                "species": "Sardinops sagax",
                "presence_only": True,
                "weight_kg": None,
                "count_raised_est": None,
                "subsample_count": None,
            },
            {
                "haul_id": "CPSTrawl:209901:SY:1",
                "species": "Engraulis mordax",
                "presence_only": False,
                "weight_kg": 12.0,
                "count_raised_est": 100,
                "subsample_count": 10,
            },
        ]
    )
    obs, stats = build_trawl_observations(catch, medians=medians)
    assert stats["presence_only_excluded"] == 1
    assert len(obs) == 0


def test_juvenile_median_length_excluded() -> None:
    medians = median_length_by_event_species(
        pd.DataFrame(
            [
                {
                    "event_id": "CPSTrawl:209901:SY:2",
                    "species": "Sardinops sagax",
                    "length_mm": 90.0,
                },
                {
                    "event_id": "CPSTrawl:209901:SY:2",
                    "species": "Sardinops sagax",
                    "length_mm": 100.0,
                },
            ]
        )
    )
    catch = pd.DataFrame(
        [
            {
                "haul_id": "CPSTrawl:209901:SY:2",
                "species": "Sardinops sagax",
                "presence_only": False,
                "weight_kg": 5.0,
                "count_raised_est": 50,
                "subsample_count": 5,
            }
        ]
    )
    obs, stats = build_trawl_observations(catch, medians=medians)
    assert stats["juvenile_excluded"] == 1
    assert obs.empty


def test_implied_absence_for_enumerated_haul_without_target_row() -> None:
    medians = median_length_by_event_species(
        pd.DataFrame(
            [
                {
                    "event_id": "CPSTrawl:209901:SY:3",
                    "species": "Engraulis mordax",
                    "length_mm": 110.0,
                }
            ]
        )
    )
    catch = pd.DataFrame(
        [
            {
                "haul_id": "CPSTrawl:209901:SY:3",
                "species": "Engraulis mordax",
                "presence_only": False,
                "weight_kg": 1.0,
                "count_raised_est": 10,
                "subsample_count": 10,
            }
        ]
    )
    obs, _ = build_trawl_observations(catch, medians=medians)
    full, stats = append_implied_absence_observations(
        obs,
        trawl_catch=catch,
        nearshore_catch=pd.DataFrame(),
    )
    assert stats["implied_absences_trawl"] == 1
    sardine = full[full["species"] == "Sardinops sagax"]
    assert len(sardine) == 1
    assert int(sardine.iloc[0]["encounter"]) == 0


def test_adult_trawl_and_nearshore_observations(tmp_path: Path) -> None:
    trawl_spec = tmp_path / "trawl_spec.parquet"
    near_spec = tmp_path / "near_spec.parquet"
    trawl_catch = tmp_path / "trawl_catch.parquet"
    near_catch = tmp_path / "near_catch.parquet"

    pd.DataFrame(
        [
            {
                "event_id": "CPSTrawl:209901:SY:1",
                "species": "Sardinops sagax",
                "length_mm": 165.0,
            },
            {
                "event_id": "CPSNearshore:209901:SY:1",
                "species": "Engraulis mordax",
                "length_mm": 100.0,
            },
        ]
    ).to_parquet(trawl_spec, index=False)
    pd.DataFrame(
        [
            {
                "event_id": "CPSNearshore:209901:SY:1",
                "species": "Engraulis mordax",
                "length_mm": 100.0,
            }
        ]
    ).to_parquet(near_spec, index=False)

    pd.DataFrame(
        [
            {
                "haul_id": "CPSTrawl:209901:SY:1",
                "species": "Sardinops sagax",
                "presence_only": False,
                "weight_kg": 20.0,
                "count_raised_est": 200,
                "subsample_count": 20,
            }
        ]
    ).to_parquet(trawl_catch, index=False)
    pd.DataFrame(
        [
            {
                "set_id": "CPSNearshore:209901:SY:1",
                "scientific_name": "Engraulis mordax",
                "total_number": 500,
                "total_weight_kg": 40.0,
            }
        ]
    ).to_parquet(near_catch, index=False)

    obs, summary = assemble_adult_observations(
        trawl_catch_path=trawl_catch,
        nearshore_catch_path=near_catch,
        trawl_specimens_path=trawl_spec,
        nearshore_specimens_path=near_spec,
    )
    assert summary["presence_only_excluded_total"] == 0
    assert len(obs) == 2
    sources = set(obs["observation_source"])
    assert sources == {OBSERVATION_SOURCE_TRAWL, OBSERVATION_SOURCE_NEARSHORE}


def test_point_event_covariates_do_not_drop_too_few_track_points() -> None:
    store = glorys_store_from_synthetic_days([GLORYS_TEST_DAY])
    event = pd.Series(
        {
            "start_latitude": 33.0,
            "start_longitude": -120.0,
            "stop_latitude": 33.0,
            "stop_longitude": -120.0,
            "start_time": pd.Timestamp("2021-07-01T12:00:00Z"),
            "stop_time": pd.Timestamp("2021-07-01T12:00:00Z"),
        }
    )
    cov, reasons = mean_covariates_along_segment(event, store.field_sampler)
    assert DROP_REASON_TOO_FEW_TRACK_POINTS not in reasons
    assert cov["T3m"] == pytest.approx(18.0, rel=0.05)


def test_build_adult_training_table_joins_glorys(tmp_path: Path) -> None:
    hauls = trawl_hauls_to_physics_events(_synthetic_trawl_haul())
    sets = nearshore_sets_to_physics_events(_synthetic_nearshore_set())
    events = pd.concat([hauls, sets], ignore_index=True)
    observations = pd.DataFrame(
        [
            {
                "event_id": "CPSTrawl:209901:SY:1",
                "species": "Sardinops sagax",
                "observation_source": OBSERVATION_SOURCE_TRAWL,
                "encounter": 1,
                "weight_kg": 10.0,
                "count_observed": 100,
                "adult_median_length_mm": 165.0,
                "biology_excluded": False,
                "biology_excluded_reason": "",
            },
            {
                "event_id": "CPSNearshore:209901:SY:1",
                "species": "Engraulis mordax",
                "observation_source": OBSERVATION_SOURCE_NEARSHORE,
                "encounter": 1,
                "weight_kg": 5.0,
                "count_observed": 50,
                "adult_median_length_mm": 100.0,
                "biology_excluded": False,
                "biology_excluded_reason": "",
            },
        ]
    )
    store = glorys_store_from_synthetic_days([GLORYS_TEST_DAY])
    table, qc, _drops = build_adult_cps_training_table(
        events,
        observations,
        store,
        drops_parquet_path=tmp_path / "drops.parquet",
        drop_summary_json_path=tmp_path / "drops.json",
    )
    assert qc["observation_rows"] == 2
    assert COL_EVENT_ID in table.columns
    assert table["T3m"].notna().all()
    assert set(table["observation_source"]) == {
        OBSERVATION_SOURCE_TRAWL,
        OBSERVATION_SOURCE_NEARSHORE,
    }
    assert table["excluded"].eq(False).all()


def test_adult_cutoffs_documented() -> None:
    assert ADULT_MIN_LENGTH_MM["Sardinops sagax"] == 160.0
    assert ADULT_MIN_LENGTH_MM["Engraulis mordax"] == 98.0
