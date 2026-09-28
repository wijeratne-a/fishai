"""Common-support filtering across all four model rows."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from fishai.scoring.harmonization.constants import ALL_MODEL_ROWS


def apply_common_support(
    df: pd.DataFrame,
    model_columns: Iterable[str] = ALL_MODEL_ROWS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Keep rows where every model column is finite.

    Returns (kept, dropped) where dropped rows include ``nearshore`` for reporting.
    """
    cols = list(model_columns)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"model columns missing from pairing table: {missing}")
    finite = df[cols].apply(pd.to_numeric, errors="coerce").notna().all(axis=1)
    kept = df.loc[finite].copy()
    dropped = df.loc[~finite].copy()
    return kept, dropped


def insufficient_coverage_counts(dropped: pd.DataFrame) -> dict[str, int]:
    if dropped.empty or "nearshore" not in dropped.columns:
        return {"nearshore": 0, "offshore": 0, "total": int(len(dropped))}
    near = int(dropped["nearshore"].astype(bool).sum())
    total = int(len(dropped))
    return {"nearshore": near, "offshore": total - near, "total": total}
