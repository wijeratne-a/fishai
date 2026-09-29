"""Tests for ``training_exclusion_audit``."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fishai.ingestion.physics.training_exclusion_audit import run_training_exclusion_audit


def test_training_exclusion_audit_smoke(tmp_path: Path) -> None:
    training = tmp_path / "train.parquet"
    events = tmp_path / "events.parquet"
    counts = tmp_path / "counts.parquet"
    drops = tmp_path / "drops.parquet"

    pd.DataFrame(
        [
            {
                "event_id": "E1",
                "T3m": 1.0,
                "S3m": 1.0,
                "MLD_m": 1.0,
                "sst_grad": 1.0,
                "front_distance_km": 1.0,
                "upwelling": float("nan"),
                "upwelling_status": "",
                "bottom_depth_m": 150.0,
                "depth_at_model_floor": False,
                "source": "glorys",
                "provenance": "test",
                "excluded": False,
                "source_product": "cmems_mod_glo_phy_my_0.083deg_P1D-m",
                "excluded_reason": "",
            },
            {
                "event_id": "E2",
                "T3m": float("nan"),
                "S3m": float("nan"),
                "MLD_m": float("nan"),
                "sst_grad": float("nan"),
                "front_distance_km": float("nan"),
                "upwelling": float("nan"),
                "upwelling_status": "",
                "bottom_depth_m": float("nan"),
                "depth_at_model_floor": False,
                "source": "glorys",
                "provenance": "test",
                "excluded": True,
                "source_product": "",
                "excluded_reason": "missing_covariate",
            },
        ]
    ).to_parquet(training)

    pd.DataFrame(
        [
            {
                "event_id": "E1",
                "start_time": "2020-01-01T12:00:00+00:00",
                "stop_time": "2020-01-01T12:30:00+00:00",
                "start_latitude": 33.0,
                "start_longitude": -120.0,
                "stop_latitude": 33.01,
                "stop_longitude": -119.99,
            },
            {
                "event_id": "E2",
                "start_time": "2020-01-02T12:00:00+00:00",
                "stop_time": "2020-01-02T12:30:00+00:00",
                "start_latitude": 33.0,
                "start_longitude": -120.0,
                "stop_latitude": 33.01,
                "stop_longitude": -119.99,
            },
        ]
    ).to_parquet(events)

    pd.DataFrame(
        [
            {"event_id": "E1", "taxon": "sardine", "count": 1},
            {"event_id": "E1", "taxon": "anchovy", "count": 0},
            {"event_id": "E2", "taxon": "sardine", "count": 0},
            {"event_id": "E2", "taxon": "anchovy", "count": 2},
        ]
    ).to_parquet(counts)

    pd.DataFrame(
        [
            {
                "event_id": "E2",
                "reason": "missing_covariate",
                "covariate": "MLD_m",
                "latitude": 33.0,
                "longitude": -120.0,
            }
        ]
    ).to_parquet(drops)

    report = run_training_exclusion_audit(
        training_path=training,
        events_path=events,
        counts_path=counts,
        drops_path=drops,
    )
    assert report["row_count"] == 2
    assert report["kept_count"] == 1
    assert report["excluded_count"] == 1
    assert report["missing_covariate_audit"]["missing_by_covariate_unique_events"]["MLD_m"] == 1
    json.loads(json.dumps(report))
