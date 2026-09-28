"""Common-support filtering tests."""

from __future__ import annotations

import pandas as pd

from fishai.scoring.harmonization.common_support import (
    apply_common_support,
    insufficient_coverage_counts,
)
from fishai.scoring.harmonization.constants import ALL_MODEL_ROWS


def test_common_support_and_insufficient_coverage_counts() -> None:
    df = pd.DataFrame(
        {
            "nearshore": [True, False, True],
            "wcofs_native": [1.0, 2.0, float("nan")],
            "wcofs_coarsened": [1.1, 2.1, 3.0],
            "wcofs_coarsened_mapped": [1.2, 2.2, 3.1],
            "glorys": [1.0, 2.0, 3.0],
        }
    )
    kept, dropped = apply_common_support(df)
    assert len(kept) == 2
    assert len(dropped) == 1
    counts = insufficient_coverage_counts(dropped)
    assert counts == {"nearshore": 1, "offshore": 0, "total": 1}


def test_all_rows_share_nearshore_and_n() -> None:
    df = pd.DataFrame(
        {
            "date": ["2025-10-01"] * 4,
            "variable": ["sea_water_temperature"] * 4,
            "obs_value": [15.0, 15.0, 15.0, 15.0],
            "nearshore": [True, True, False, False],
            "obs_id": ["b1", "b2", "b3", "b4"],
            "wcofs_native": [14.0, 14.5, 15.0, 15.5],
            "wcofs_coarsened": [14.1, 14.6, 15.1, 15.6],
            "wcofs_coarsened_mapped": [14.2, 14.7, 15.2, 15.7],
            "glorys": [14.0, 14.5, 15.0, 15.5],
        }
    )
    kept, _ = apply_common_support(df)
    for near in (True, False):
        sub = kept[kept["nearshore"] == near]
        for col in ALL_MODEL_ROWS:
            assert len(sub) == len(sub[col].dropna())
