"""Write harmonization holdout score artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def write_holdout_outputs(
    out_dir: Path,
    detail_df: pd.DataFrame,
    summary: dict[str, Any],
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = out_dir / "holdout_scores.parquet"
    summary_path = out_dir / "summary.json"
    detail_df.to_parquet(parquet_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return parquet_path, summary_path
