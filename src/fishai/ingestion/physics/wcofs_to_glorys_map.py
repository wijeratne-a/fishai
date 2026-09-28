"""
WCOFS-to-GLORYS correction map (``wcofs_coarsened_mapped`` row).

Fits per-variable, per-stratum ordinary least squares on the overlap fit split only:
``y_glorys = a + b * x_wcofs`` with strata ``nearshore`` and ``offshore``.
A seasonal harmonic extension is reserved but disabled by default (``use_seasonal_harmonic=False``).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config, split_label
from fishai.ingestion.sources import REPO_ROOT

DEFAULT_MAP_VERSION_DIR = REPO_ROOT / "artifacts" / "harmonization" / "wcofs_to_glorys_map" / "v1"
CORRECTION_MAP_FILENAME = "correction_map.json"
CORRECTION_MAP_HASH_FILENAME = "correction_map.sha256"
MANIFEST_FILENAME = "manifest.json"

MAPPED_VARIABLES: tuple[str, ...] = (
    "T3m",
    "S3m",
    "MLD_m",
    "sst_grad",
    "front_distance_km",
)
PASSTHROUGH_VARIABLES: tuple[str, ...] = ("upwelling", "u_surf", "v_surf")
STRATA: tuple[str, ...] = ("nearshore", "offshore")

MAP_SCHEMA_VERSION = 1
FUNCTIONAL_FORM = "per_variable_per_stratum_linear_ols"


class HarmonizationMapLeakageError(RuntimeError):
    """Raised when test-period rows would enter the fit split."""


class HarmonizationMapHashError(RuntimeError):
    """Raised when a frozen correction map fails SHA-256 verification."""


def _code_version() -> str:
    try:
        return version("fishai")
    except Exception:
        return "unknown"


def _git_head_sha() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def fit_date_range_from_config(config: dict[str, Any]) -> tuple[dt.date, dt.date]:
    split = config["split"]
    fit_start = split.get("fit_start") or config["overlap"]["start"]
    return (
        dt.date.fromisoformat(str(fit_start)),
        dt.date.fromisoformat(str(split["fit_end"])),
    )


def test_period_start_from_config(config: dict[str, Any]) -> dt.date:
    return dt.date.fromisoformat(str(config["split"]["test_start"]))


def assert_fit_split_only(df: pd.DataFrame, config: dict[str, Any]) -> None:
    """Hard-fail if any overlap row on or after the test window enters fitting."""
    if "day" not in df.columns:
        raise ValueError("overlap frame must include a day column")
    days = pd.to_datetime(df["day"]).dt.date
    fit_end = fit_date_range_from_config(config)[1]
    test_start = test_period_start_from_config(config)
    if "split" in df.columns:
        bad_split = df["split"] == "test"
        if bad_split.any():
            raise HarmonizationMapLeakageError(
                f"fit split contains {int(bad_split.sum())} rows labeled test"
            )
    late = days > fit_end
    if late.any():
        raise HarmonizationMapLeakageError(
            f"fit split contains {int(late.sum())} rows after fit_end {fit_end.isoformat()}"
        )
    in_test_window = days >= test_start
    if in_test_window.any():
        raise HarmonizationMapLeakageError(
            f"fit split contains {int(in_test_window.sum())} rows on or after test_start "
            f"{test_start.isoformat()}"
        )


def _ols_intercept_slope(x: np.ndarray, y: np.ndarray) -> dict[str, float | int]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    n = int(mask.sum())
    if n < 2:
        return {"a": float("nan"), "b": float("nan"), "n": n}
    xv = x[mask]
    yv = y[mask]
    xm = float(np.mean(xv))
    ym = float(np.mean(yv))
    var = float(np.mean((xv - xm) ** 2))
    if var <= 0.0:
        return {"a": float(ym - xm), "b": 1.0, "n": n}
    cov = float(np.mean((xv - xm) * (yv - ym)))
    b = cov / var
    a = ym - b * xm
    return {"a": float(a), "b": float(b), "n": n}


def fit_correction_map_from_overlap(
    df: pd.DataFrame,
    *,
    config: dict[str, Any] | None = None,
    use_seasonal_harmonic: bool = False,
    fitting_commit_sha: str | None = None,
    fit_split_parquet_sha256: str | None = None,
    prereg_commit_sha: str | None = None,
) -> dict[str, Any]:
    """
    Fit the correction map from an overlap pairing table (fit split rows only).

    ``use_seasonal_harmonic`` is intentionally off by default; enabling it is not
    implemented in this pilot delivery (auditor sign-off required before use).
    """
    if use_seasonal_harmonic:
        raise NotImplementedError(
            "seasonal harmonic correction is disabled; set use_seasonal_harmonic=False"
        )
    config = config or load_overlap_config()
    fit_start, fit_end = fit_date_range_from_config(config)
    if "split" in df.columns and (df["split"] == "test").any():
        raise HarmonizationMapLeakageError(
            f"overlap frame includes {int((df['split'] == 'test').sum())} test-split rows"
        )
    work = df.copy()
    if "split" in work.columns:
        work = work.loc[work["split"] == "fit"]
    else:
        days = pd.to_datetime(work["day"]).dt.date
        work = work.loc[days <= fit_end]
    assert_fit_split_only(work, config)
    if "nearshore" not in work.columns:
        raise ValueError("overlap frame must include nearshore for stratum fitting")

    coefficients: dict[str, dict[str, dict[str, float | int]]] = {}
    for var in MAPPED_VARIABLES:
        x_col = f"wcofs_{var}"
        y_col = f"glorys_{var}"
        if x_col not in work.columns or y_col not in work.columns:
            raise ValueError(f"overlap frame missing {x_col} or {y_col}")
        coefficients[var] = {}
        for stratum, flag in (("nearshore", True), ("offshore", False)):
            sub = work.loc[work["nearshore"] == flag]
            coefficients[var][stratum] = _ols_intercept_slope(
                sub[x_col].to_numpy(),
                sub[y_col].to_numpy(),
            )

    return {
        "schema_version": MAP_SCHEMA_VERSION,
        "functional_form": FUNCTIONAL_FORM,
        "seasonal_harmonic": False,
        "code_version": _code_version(),
        "fit_date_range": {
            "fit_start": fit_start.isoformat(),
            "fit_end": fit_end.isoformat(),
        },
        "variables_mapped": list(MAPPED_VARIABLES),
        "coefficients": coefficients,
        "metadata": {
            "fitting_commit_sha": fitting_commit_sha or _git_head_sha(),
            "fit_split_parquet_sha256": fit_split_parquet_sha256,
            "prereg_commit_sha": prereg_commit_sha,
        },
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_correction_map_artifacts(
    map_doc: dict[str, Any],
    directory: Path | str | None = None,
    *,
    fit_split_parquet_sha256: str | None = None,
) -> dict[str, Path]:
    """Write ``correction_map.json``, sidecar hash, and ``manifest.json``."""
    directory = Path(directory) if directory is not None else DEFAULT_MAP_VERSION_DIR
    directory.mkdir(parents=True, exist_ok=True)
    map_path = directory / CORRECTION_MAP_FILENAME
    map_path.write_text(json.dumps(map_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = sha256_file(map_path)
    hash_path = directory / CORRECTION_MAP_HASH_FILENAME
    hash_path.write_text(f"{digest}\n", encoding="utf-8")

    meta = map_doc.get("metadata") or {}
    fit_range = map_doc.get("fit_date_range") or {}
    manifest = {
        "fitting_commit_sha": meta.get("fitting_commit_sha"),
        "fit_split_parquet_sha256": fit_split_parquet_sha256 or meta.get("fit_split_parquet_sha256"),
        "prereg_commit_sha": meta.get("prereg_commit_sha"),
        "variables_mapped": map_doc.get("variables_mapped"),
        "fit_date_range": fit_range,
        "correction_map_file": CORRECTION_MAP_FILENAME,
        "correction_map_sha256": digest,
        "functional_form": map_doc.get("functional_form"),
        "seasonal_harmonic": map_doc.get("seasonal_harmonic", False),
        "code_version": map_doc.get("code_version"),
    }
    manifest_path = directory / MANIFEST_FILENAME
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"map": map_path, "hash": hash_path, "manifest": manifest_path}


def load_correction_map(
    directory: Path | str | None = None,
    *,
    verify_hash: bool = True,
) -> dict[str, Any]:
    """Load a frozen correction map, optionally verifying ``correction_map.sha256``."""
    directory = Path(directory) if directory is not None else DEFAULT_MAP_VERSION_DIR
    map_path = directory / CORRECTION_MAP_FILENAME
    if not map_path.is_file():
        raise FileNotFoundError(f"correction map not found: {map_path}")
    if verify_hash:
        hash_path = directory / CORRECTION_MAP_HASH_FILENAME
        if not hash_path.is_file():
            raise HarmonizationMapHashError(f"missing hash sidecar: {hash_path}")
        expected = hash_path.read_text(encoding="utf-8").strip().split()[0]
        actual = sha256_file(map_path)
        if actual != expected:
            raise HarmonizationMapHashError(
                f"correction map hash mismatch (expected {expected}, got {actual})"
            )
    return json.loads(map_path.read_text(encoding="utf-8"))


def apply_map(
    wcofs_fields: dict[str, np.ndarray],
    nearshore: np.ndarray,
    map_doc: dict[str, Any],
) -> dict[str, np.ndarray]:
    """
    Apply the frozen map to coarsened WCOFS covariate fields on the GLORYS grid.

    Produces the ``wcofs_coarsened_mapped`` physics row. ``upwelling``, ``u_surf``, and
    ``v_surf`` pass through unchanged when present. Missing values are never filled.
    """
    coeffs = map_doc["coefficients"]
    nearshore_arr = np.asarray(nearshore, dtype=bool)
    out: dict[str, np.ndarray] = {}
    for var in MAPPED_VARIABLES:
        if var not in wcofs_fields:
            raise KeyError(f"missing coarsened WCOFS field {var}")
        x = np.asarray(wcofs_fields[var], dtype=float)
        mapped = np.full(x.shape, np.nan, dtype=float)
        for stratum, mask in (("nearshore", nearshore_arr), ("offshore", ~nearshore_arr)):
            c = coeffs[var][stratum]
            a, b = float(c["a"]), float(c["b"])
            sel = mask & np.isfinite(x)
            mapped[sel] = a + b * x[sel]
        out[var] = mapped
    for key in PASSTHROUGH_VARIABLES:
        if key in wcofs_fields:
            out[key] = np.asarray(wcofs_fields[key])
    return out


def apply_map_to_overlap_frame(
    df: pd.DataFrame,
    map_doc: dict[str, Any],
    *,
    prefix: str = "mapped_",
) -> pd.DataFrame:
    """Vectorized map application for overlap / training tables (one row per cell-day)."""
    coeffs = map_doc["coefficients"]
    out = df.copy()
    nearshore = out["nearshore"].to_numpy(dtype=bool)
    for var in MAPPED_VARIABLES:
        x_col = f"wcofs_{var}"
        target = f"{prefix}{var}"
        x = out[x_col].to_numpy(dtype=float)
        y = np.full(x.shape, np.nan, dtype=float)
        for stratum, mask in (("nearshore", nearshore), ("offshore", ~nearshore)):
            c = coeffs[var][stratum]
            a, b = float(c["a"]), float(c["b"])
            sel = mask & np.isfinite(x)
            y[sel] = a + b * x[sel]
        out[target] = y
    for key in PASSTHROUGH_VARIABLES:
        src = f"wcofs_{key}"
        if src in out.columns:
            out[f"{prefix}{key}"] = out[src]
    return out


def load_prereg_fit_window() -> tuple[dt.date, dt.date]:
    """Fit window from ``prereg/harmonization_wcofs_glorys.yaml``."""
    path = REPO_ROOT / "prereg" / "harmonization_wcofs_glorys.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    block = raw["harmonization_wcofs_glorys"]["temporal_split"]
    return (
        dt.date.fromisoformat(str(block["fit_start"])),
        dt.date.fromisoformat(str(block["fit_end"])),
    )


def overlap_day_in_fit(day: dt.date, config: dict[str, Any] | None = None) -> bool:
    config = config or load_overlap_config()
    return split_label(day, config) == "fit"
