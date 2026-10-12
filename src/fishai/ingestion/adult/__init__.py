"""Adult CPS training table (trawl + nearshore observations × GLORYS covariates)."""

from fishai.ingestion.adult.constants import (
    ADULT_MIN_LENGTH_MM,
    DEFAULT_PROCESSED_DIR,
    DEFAULT_TRAINING_TABLE_PATH,
)
from fishai.ingestion.adult.training_build import (
    build_adult_cps_training_table,
    run_build_adult_cps_training_table,
)

__all__ = [
    "ADULT_MIN_LENGTH_MM",
    "DEFAULT_PROCESSED_DIR",
    "DEFAULT_TRAINING_TABLE_PATH",
    "build_adult_cps_training_table",
    "run_build_adult_cps_training_table",
]
