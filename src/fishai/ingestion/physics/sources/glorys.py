"""Copernicus Marine GLORYS reanalysis (licence-gated; training/hindcast only)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Callable

import numpy as np

from fishai.ingestion.copernicus_compliance import (
    append_pull_log,
    build_pull_record,
    glorys_attribution_bundle,
)
from fishai.ingestion.physics.glorys_catalog import resolve_glorys_dataset_for_date
from fishai.ingestion.physics.vertical import (
    CUFES_SAMPLE_DEPTH_M,
    interp_at_depth_from_z_levels,
    mld,
)
from fishai.ingestion.sources import SourceNotApprovedError, require_approved

SOURCE_MODULE = "glorys"

PRODUCT_ID_MY = "cmems_mod_glo_phy_my_0.083deg_P1D-m"
# Deprecated interim id (not in live catalogue); kept for explicit mismatch tests only.
PRODUCT_ID_MYINT = "cmems_mod_glo_phy_myint_0.083deg_P1D-m"
PRODUCT_ID = PRODUCT_ID_MY

MY_PRODUCT_START = dt.date(1993, 1, 1)
MY_COVERAGE_END_DEFAULT = dt.date(2026, 6, 23)

PRODUCT_TIME_START = MY_PRODUCT_START
PRODUCT_TIME_END = MY_COVERAGE_END_DEFAULT
LICENSE_VALID_UNTIL = dt.date(2028, 6, 30)

VARIABLES = ("thetao", "so", "bottomT", "mlotst", "uo", "vo", "zos")

ALLOWED_PURPOSES = frozenset({"training", "hindcast"})


def _config_date(value: Any) -> dt.date:
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def glorys_product_for_date(
    date: dt.date,
    *,
    config: dict[str, Any] | None = None,
) -> str:
    """
    Copernicus Marine GLORYS12 dataset id for ``date``.

    Resolved from the live Copernicus Marine catalogue time coverage (cached per run).
    Raises ``GlorysCatalogError`` with a ``reason_code`` when the catalogue cannot be
    used or no dataset covers ``date``.
    """
    del config  # catalogue coverage is authoritative; config retained for call-site compat
    if date < MY_PRODUCT_START:
        raise ValueError(
            f"glorys: date {date} is before {MY_PRODUCT_START} (my product start)"
        )
    return resolve_glorys_dataset_for_date(date).dataset_id


def glorys_dataset_id_for_date(
    date: dt.date,
    dataset_id: str | None = None,
    *,
    config: dict[str, Any] | None = None,
) -> str:
    """
    Canonical Copernicus dataset id for ``date``.

    When ``dataset_id`` is provided it must equal ``glorys_product_for_date(date)``;
    otherwise ``ValueError`` is raised.
    """
    expected = glorys_product_for_date(date, config=config)
    if dataset_id is not None and dataset_id != expected:
        raise ValueError(
            f"glorys: dataset_id {dataset_id!r} does not match glorys_product_for_date("
            f"{date!r}) (expected {expected!r})"
        )
    return expected


def resolve_glorys_product_id(
    day: dt.date,
    config: dict[str, Any] | None = None,
    *,
    dataset_id: str | None = None,
) -> str:
    """Resolve GLORYS dataset id for overlap pairing and pull logs (date-based)."""
    return glorys_dataset_id_for_date(day, dataset_id, config=config)


def _pull_log_path(entry: dict[str, Any]) -> Path:
    rel = entry.get("pull_log_path") or "data/provenance/copernicus_pull_log.jsonl"
    path = Path(rel)
    if not path.is_absolute():
        from fishai.ingestion.sources import REPO_ROOT

        path = REPO_ROOT / path
    return path


def fetch_day(
    date: dt.date,
    bbox: tuple[float, float, float, float],
    variables: tuple[str, ...] = VARIABLES,
    *,
    purpose: str = "training",
    fetch_fn: Callable[[], Any] | None = None,
    log_path: Path | None = None,
    path: Path | None = None,
    dataset_id: str | None = None,
    config: dict[str, Any] | None = None,
) -> Any:
    """
    Fetch GLORYS for ``date`` (Copernicus Toolbox on runtime hosts only).

    Credentials are personal, non-transferable, and live only under the runtime
    Copernicus Marine config directory. This code never reads, logs, or prints
    credential material. CI uses ``fetch_fn`` mocks exclusively.
    """
    entry = require_approved("glorys", purpose=purpose, path=path)
    if purpose not in ALLOWED_PURPOSES:
        raise SourceNotApprovedError(f"glorys: unsupported purpose {purpose!r}")
    if dt.date.today() > LICENSE_VALID_UNTIL:
        raise SourceNotApprovedError("glorys: licence validity ended")

    resolution = resolve_glorys_dataset_for_date(date)
    ds_id = glorys_dataset_id_for_date(date, dataset_id, config=config)
    record = build_pull_record(
        dataset_id=ds_id,
        date_start=date.isoformat(),
        date_end=date.isoformat(),
        variables=variables,
        bbox=bbox,
        request_count=1,
    )
    record.update(resolution.pull_log_fields())
    append_pull_log(record, log_path=log_path or _pull_log_path(entry))

    if fetch_fn is None:
        raise RuntimeError(
            "glorys: live Copernicus client not invoked from unit tests; inject fetch_fn"
        )
    payload = fetch_fn()
    attrs = glorys_attribution_bundle(entry)
    if isinstance(payload, dict):
        payload.setdefault("metadata", {}).update(attrs)
        payload["metadata"]["glorys_derived"] = True
    return payload


def glorys_column_features(
    z_levels_m: np.ndarray,
    temp_profile: np.ndarray,
    salt_profile: np.ndarray,
    mlotst_native: float | None,
) -> dict[str, float]:
    """
    Build depth features for one GLORYS column.

    T3m/S3m use linear interpolation to exactly 3 m. MLD uses the shared 0.2 °C
    temperature-threshold rule. ``mlotst`` is returned only as a cross-check.
    """
    z = -np.asarray(z_levels_m, dtype=float)
    temp = np.asarray(temp_profile, dtype=float)
    salt = np.asarray(salt_profile, dtype=float)
    z3d = z[:, None, None]
    t3d = temp[:, None, None]
    mld_m = float(mld(z3d, t3d)[0, 0])
    out = {
        "T3m": interp_at_depth_from_z_levels(z_levels_m, temp, CUFES_SAMPLE_DEPTH_M),
        "S3m": interp_at_depth_from_z_levels(z_levels_m, salt, CUFES_SAMPLE_DEPTH_M),
        "MLD_m": mld_m,
        "mlotst_crosscheck": float(mlotst_native) if mlotst_native is not None else float("nan"),
    }
    return out
