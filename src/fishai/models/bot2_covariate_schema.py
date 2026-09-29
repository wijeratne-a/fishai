"""Compare bot2 training covariate schema (read-only branch) to PR #5 load_model_data expectations."""

from __future__ import annotations

import ast
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
BOT2_BRANCH = "origin/cursor/cufes-glorys-training-covariates-faff"
BOT2_MODULE = "src/fishai/ingestion/physics/cufes_training_covariates.py"
COVARIATES_MODULE = "src/fishai/ingestion/physics/covariates.py"

# Columns #5 must read for GLORYS training (configs/models + data.R upstream map).
SDMTMB_COVARIATE_REQUIRED = (
    "event_id",
    "T3m",
    "S3m",
    "MLD_m",
    "sst_grad",
    "front_distance_km",
    "upwelling",
    "excluded",
    "source_product",
)

# Depth enters models as log_depth_z upstream or bottom_depth_m (bot2); dry-run maps bottom_depth_m.
SDMTMB_DEPTH_UPSTREAM_OPTIONS = ("log_depth_z", "bottom_depth_m")

BOT2_BRANCH_REF = "cursor/cufes-glorys-training-covariates-faff"


@dataclass
class SchemaMismatch:
    kind: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "detail": self.detail}


@dataclass
class SchemaCompareResult:
    bot2_columns: tuple[str, ...] = ()
    mismatches: list[SchemaMismatch] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.mismatches


def _git_show(ref: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git show {ref}:{path} failed: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return proc.stdout


def _parse_tuple_constant(source: str, name: str) -> tuple[str, ...]:
    mod = ast.parse(source)
    for node in mod.body:
        targets: list[ast.expr] = []
        value = None
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target]
            value = node.value
        for target in targets:
            if isinstance(target, ast.Name) and target.id == name and value is not None:
                val = ast.literal_eval(value)
                if isinstance(val, tuple):
                    return tuple(str(x) for x in val)
    raise ValueError(f"{name} not found in module source")


def bot2_training_output_columns(ref: str = BOT2_BRANCH) -> tuple[str, ...]:
    local_fields = local_cufes_covariate_fields()
    extras = (
        "upwelling_status",
        "bottom_depth_m",
        "depth_at_model_floor",
        "source",
        "provenance",
        "excluded",
        "source_product",
        "excluded_reason",
    )
    cols = ("event_id", *local_fields, *extras)
    text = _git_show(ref, BOT2_MODULE)
    if "TRAINING_OUTPUT_COLUMNS" not in text:
        raise ValueError("TRAINING_OUTPUT_COLUMNS missing on bot2 branch")
    return cols


def local_cufes_covariate_fields() -> tuple[str, ...]:
    text = (REPO_ROOT / COVARIATES_MODULE).read_text(encoding="utf-8")
    return _parse_tuple_constant(text, "CUFES_COVARIATE_FIELDS")


def compare_bot2_to_sdmtmb(*, ref: str = BOT2_BRANCH) -> SchemaCompareResult:
    bot2_cols = bot2_training_output_columns(ref=ref)
    local_fields = local_cufes_covariate_fields()
    mismatches: list[SchemaMismatch] = []

    for field_name in local_fields:
        if field_name not in bot2_cols:
            mismatches.append(
                SchemaMismatch(
                    "missing_physics_field_on_bot2",
                    f"local CUFES_COVARIATE_FIELDS {field_name!r} not in bot2 TRAINING_OUTPUT_COLUMNS",
                )
            )

    for req in SDMTMB_COVARIATE_REQUIRED:
        if req not in bot2_cols:
            mismatches.append(
                SchemaMismatch(
                    "missing_required_for_sdmtmb",
                    f"bot2 table missing column required by #5 loaders: {req!r}",
                )
            )

    if not any(c in bot2_cols for c in SDMTMB_DEPTH_UPSTREAM_OPTIONS):
        mismatches.append(
            SchemaMismatch(
                "depth_column",
                f"bot2 has neither log_depth_z nor bottom_depth_m; #5 needs one via upstream_fields",
            )
        )
    if "log_depth_z" not in bot2_cols and "bottom_depth_m" in bot2_cols:
        mismatches.append(
            SchemaMismatch(
                "depth_column_name",
                "bot2 emits bottom_depth_m (meters); production YAML still maps log_depth to log_depth_z — "
                "dry-run must set upstream_fields.log_depth: bottom_depth_m and z-score in prep",
            )
        )

    bot2_extras = set(bot2_cols) - set(SDMTMB_COVARIATE_REQUIRED) - set(local_fields)
    expected_extras = {
        "upwelling_status",
        "bottom_depth_m",
        "depth_at_model_floor",
        "source",
        "provenance",
        "excluded_reason",
    }
    unexpected = sorted(bot2_extras - expected_extras)
    if unexpected:
        mismatches.append(
            SchemaMismatch(
                "unexpected_bot2_columns",
                "columns on bot2 not documented in contract: " + ", ".join(unexpected),
            )
        )

    missing_extras = sorted(expected_extras - set(bot2_cols))
    if missing_extras:
        mismatches.append(
            SchemaMismatch(
                "missing_documented_bot2_columns",
                "expected bot2 metadata columns absent: " + ", ".join(missing_extras),
            )
        )

    prod_cov_path = REPO_ROOT / "configs/models/cufes_sardine.yaml"
    if prod_cov_path.is_file():
        text = prod_cov_path.read_text(encoding="utf-8")
        if "cufes_physics_covariates.parquet" in text:
            mismatches.append(
                SchemaMismatch(
                    "production_covariate_path",
                    "configs/models/cufes_sardine.yaml still points at wcofs physics parquet; "
                    "bot2 default is data/processed/calcofi_cufes/cufes_training_covariates.parquet",
                )
            )
        if re.search(r"log_depth:\s*log_depth_z", text):
            mismatches.append(
                SchemaMismatch(
                    "upstream_depth_mapping",
                    "production upstream_fields.log_depth is log_depth_z; bot2 supplies bottom_depth_m",
                )
            )

    return SchemaCompareResult(bot2_columns=bot2_cols, mismatches=mismatches)


def mismatches_as_dicts(result: SchemaCompareResult) -> list[dict[str, str]]:
    return [m.as_dict() for m in result.mismatches]
