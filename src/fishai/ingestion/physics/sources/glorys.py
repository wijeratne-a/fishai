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
from fishai.ingestion.sources import SourceNotApprovedError, require_approved

SOURCE_MODULE = "glorys"

PRODUCT_MY_ID = "cmems_mod_glo_phy_my_0.083deg_P1D-m"
PRODUCT_MYINT_ID = "cmems_mod_glo_phy_myint_0.083deg_P1D-m"
PRODUCT_STATIC_ID = "cmems_mod_glo_phy_my_0.083deg_static"

# Back-compat alias (multiyear reanalysis product id).
PRODUCT_ID = PRODUCT_MY_ID

PRODUCT_MY_TIME_START = dt.date(1993, 1, 1)
PRODUCT_MY_TIME_END = dt.date(2021, 6, 30)
PRODUCT_MYINT_TIME_START = dt.date(2021, 7, 1)
PRODUCT_MYINT_TIME_END = dt.date(2026, 6, 23)

PRODUCT_TIME_START = PRODUCT_MY_TIME_START
PRODUCT_TIME_END = PRODUCT_MYINT_TIME_END

LICENSE_VALID_UNTIL = dt.date(2028, 6, 30)

VARIABLES = ("thetao", "so", "bottomT", "mlotst", "uo", "vo", "zos")

ALLOWED_PURPOSES = frozenset({"training", "hindcast"})


def glorys_dataset_for_date(day: dt.date) -> tuple[str, dt.date, dt.date]:
    """Return Copernicus dataset id and that dataset's inclusive coverage for ``day``."""
    if day <= PRODUCT_MY_TIME_END:
        return PRODUCT_MY_ID, PRODUCT_MY_TIME_START, PRODUCT_MY_TIME_END
    if day >= PRODUCT_MYINT_TIME_START:
        return PRODUCT_MYINT_ID, PRODUCT_MYINT_TIME_START, PRODUCT_MYINT_TIME_END
    raise ValueError(f"glorys: date {day} falls in gap between my and myint coverage")


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
    dataset_version: str | None = None,
    file_sha256: str | None = None,
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
    dataset_id, cov_start, cov_end = glorys_dataset_for_date(date)
    if date < cov_start or date > cov_end:
        raise ValueError(f"glorys: date {date} outside {dataset_id} coverage")
    if dt.date.today() > LICENSE_VALID_UNTIL:
        raise SourceNotApprovedError("glorys: licence validity ended")

    record = build_pull_record(
        dataset_id=dataset_id,
        date_start=date.isoformat(),
        date_end=date.isoformat(),
        variables=variables,
        bbox=bbox,
        request_count=1,
        dataset_version=dataset_version,
        file_sha256=file_sha256,
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
