"""Common-support filtering across all four model rows."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from fishai.ingestion.physics.wcofs_glorys_grid import UNKNOWN_REASON_INSUFFICIENT_MODEL_COVERAGE
from fishai.scoring.harmonization.constants import ALL_MODEL_ROWS

COVERAGE_DROP_REASON = UNKNOWN_REASON_INSUFFICIENT_MODEL_COVERAGE


def apply_common_support(
    df: pd.DataFrame,
    model_columns: Iterable[str] = ALL_MODEL_ROWS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Keep rows where every model column is finite.

    Dropped rows are tagged with ``coverage_drop_reason`` =
    ``insufficient_model_coverage`` (same label as bot2 nowcast UNKNOWN).
    """
    cols = list(model_columns)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"model columns missing from pairing table: {missing}")
    finite = df[cols].apply(pd.to_numeric, errors="coerce").notna().all(axis=1)
    kept = df.loc[finite].copy()
    dropped = df.loc[~finite].copy()
    if not dropped.empty:
        dropped = dropped.copy()
        dropped["coverage_drop_reason"] = COVERAGE_DROP_REASON
    return kept, dropped


def insufficient_coverage_counts(dropped: pd.DataFrame) -> dict[str, int | str]:
    if dropped.empty or "nearshore" not in dropped.columns:
        return {
            "reason_label": COVERAGE_DROP_REASON,
            "nearshore": 0,
            "offshore": 0,
            "total": int(len(dropped)),
        }
    near = int(dropped["nearshore"].astype(bool).sum())
    total = int(len(dropped))
    return {
        "reason_label": COVERAGE_DROP_REASON,
        "nearshore": near,
        "offshore": total - near,
        "total": total,
    }
