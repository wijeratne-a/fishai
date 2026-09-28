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
from fishai.ingestion.physics.vertical import (
    CUFES_SAMPLE_DEPTH_M,
    interp_at_depth_from_z_levels,
    mld,
)
from fishai.ingestion.sources import SourceNotApprovedError, get_source_entry, require_approved

SOURCE_MODULE = "glorys"

PRODUCT_ID_MY = "cmems_mod_glo_phy_my_0.083deg_P1D-m"
PRODUCT_ID_MYINT = "cmems_mod_glo_phy_myint_0.083deg_P1D-m"
PRODUCT_ID = PRODUCT_ID_MYINT
PRODUCT_TIME_START = dt.date(1993, 1, 1)
PRODUCT_TIME_END = dt.date(2026, 6, 23)
LICENSE_VALID_UNTIL = dt.date(2028, 6, 30)

VARIABLES = ("thetao", "so", "bottomT", "mlotst", "uo", "vo", "zos")

ALLOWED_PURPOSES = frozenset({"training", "hindcast"})


def resolve_glorys_product_id(
    _day: dt.date,
    config: dict[str, Any] | None = None,
) -> str:
    """
    Copernicus Marine dataset id for GLORYS pulls on ``day``.

    No automatic switch between MY and MYINT is implemented; the overlap config
    ``glorys.product_id`` is authoritative for the pilot window.
    """
    if config is not None:
        return str(config["glorys"]["product_id"])
    return PRODUCT_ID


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
    if date < PRODUCT_TIME_START or date > PRODUCT_TIME_END:
        raise ValueError(f"glorys: date {date} outside product coverage")
    if dt.date.today() > LICENSE_VALID_UNTIL:
        raise SourceNotApprovedError("glorys: licence validity ended")

    ds_id = dataset_id or resolve_glorys_product_id(date)
    record = build_pull_record(
        dataset_id=ds_id,
        date_start=date.isoformat(),
        date_end=date.isoformat(),
        variables=variables,
        bbox=bbox,
        request_count=1,
    )
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
