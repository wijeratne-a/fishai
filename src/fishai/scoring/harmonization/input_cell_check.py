"""Cell-by-cell mapped WCOFS vs GLORYS input checks (graded vs reported-only)."""

from __future__ import annotations

from typing import Any

import pandas as pd

from fishai.scoring.harmonization.constants import VERDICT_NOT_GRADABLE
from fishai.scoring.harmonization.grading import InputCheckGradeInput, grade_input_check
from fishai.scoring.harmonization.input_check_config import (
    GRADING_STATUS_GRADED,
    graded_input_variables_from_prereg,
    variable_grading_status_map,
)


def build_input_cell_check_summary(
    doc: dict[str, Any],
    input_check_table: pd.DataFrame | None,
    stratum: str,
    cutoffs: dict[str, float],
) -> tuple[list[str], list[dict[str, Any]]]:
    """
    Return (verdicts for graded vars only, full per-variable report rows).

    Non-graded variables are reported with ``grading_status`` as the reason and
    do not contribute to ``verdicts``.
    """
    status_map = variable_grading_status_map(doc)
    graded_vars = graded_input_variables_from_prereg(doc)
    verdicts: list[str] = []
    report_rows: list[dict[str, Any]] = []

    ic = (
        input_check_table.loc[input_check_table.get("stratum", "pooled") == stratum]
        if input_check_table is not None
        else pd.DataFrame()
    )

    for var_name in graded_vars:
        grading_status = status_map.get(var_name, "")
        part = ic[ic["variable"] == var_name] if not ic.empty else pd.DataFrame()
        row: dict[str, Any] = {
            "stratum": stratum,
            "variable": var_name,
            "grading_status": grading_status,
            "verdict": None,
            "reason": None,
            "rmse": None,
            "glorys_spatial_sd": None,
        }
        if part.empty:
            verdicts.append(VERDICT_NOT_GRADABLE)
            row["verdict"] = VERDICT_NOT_GRADABLE
            row["reason"] = "missing_input_check_row"
            report_rows.append(row)
            continue
        rec = part.iloc[0]
        rmse = float(rec["rmse"])
        sd = float(rec["glorys_spatial_sd"])
        row["rmse"] = rmse
        row["glorys_spatial_sd"] = sd
        verdict = grade_input_check(InputCheckGradeInput(rmse=rmse, glorys_spatial_sd=sd), cutoffs)
        row["verdict"] = verdict
        verdicts.append(verdict)
        report_rows.append(row)

    for var_name, grading_status in sorted(status_map.items()):
        if grading_status == GRADING_STATUS_GRADED:
            continue
        part = ic[ic["variable"] == var_name] if not ic.empty else pd.DataFrame()
        row = {
            "stratum": stratum,
            "variable": var_name,
            "grading_status": grading_status,
            "verdict": None,
            "reason": grading_status,
            "rmse": None,
            "glorys_spatial_sd": None,
        }
        if not part.empty:
            row["rmse"] = float(part.iloc[0]["rmse"])
            row["glorys_spatial_sd"] = float(part.iloc[0]["glorys_spatial_sd"])
        report_rows.append(row)

    return verdicts, report_rows
