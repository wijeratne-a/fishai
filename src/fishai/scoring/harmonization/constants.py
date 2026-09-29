"""Identifiers and row labels for harmonization holdout scoring."""

from __future__ import annotations

MODEL_ROW_WCOFS_NATIVE = "wcofs_native"
MODEL_ROW_WCOFS_COARSENED = "wcofs_coarsened"
MODEL_ROW_WCOFS_COARSENED_MAPPED = "wcofs_coarsened_mapped"
MODEL_ROW_GLORYS = "glorys"

ALL_MODEL_ROWS: tuple[str, ...] = (
    MODEL_ROW_WCOFS_NATIVE,
    MODEL_ROW_WCOFS_COARSENED,
    MODEL_ROW_WCOFS_COARSENED_MAPPED,
    MODEL_ROW_GLORYS,
)

GRADED_MODEL_ROW = MODEL_ROW_WCOFS_COARSENED_MAPPED

# Re-export for callers; canonical list lives in input_check_config.
from fishai.scoring.harmonization.input_check_config import SCORER_GRADED_INPUT_VARIABLES

INPUT_CHECK_VARIABLES = SCORER_GRADED_INPUT_VARIABLES

VERDICT_PASS = "PASS"
VERDICT_DEGRADED = "DEGRADED"
VERDICT_FAIL = "FAIL"
VERDICT_UNKNOWN = "UNKNOWN"
VERDICT_NOT_GRADABLE = "not_gradable"

FAIL_EVIDENCE_REASON = "nowcast_forcing_failed_holdout"
NO_INDEPENDENT_VALIDATION_REASON = "no_independent_validation"
BUOY_INSUFFICIENT_OBS_REASON = "no_independent_obs_check"
