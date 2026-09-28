"""Copernicus Marine catalog metadata for GLORYS dataset selection (describe-backed)."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Callable, Literal

PRODUCT_ID_MY = "cmems_mod_glo_phy_my_0.083deg_P1D-m"
PRODUCT_ID_MYINT = "cmems_mod_glo_phy_myint_0.083deg_P1D-m"

CatalogStatus = Literal["found", "dataset_not_found"]
REASON_GLORYS_DATE_NOT_COVERED = "glorys_date_not_covered"
REASON_GLORYS_CATALOG_DATASET_NOT_FOUND = "glorys_catalog_dataset_not_found"


class GlorysDatasetNotCoveredError(LookupError):
    """No configured GLORYS dataset covers the requested UTC calendar day."""

    def __init__(self, day: dt.date, message: str, *, reason_code: str) -> None:
        super().__init__(message)
        self.day = day
        self.reason_code = reason_code


@dataclass(frozen=True)
class GlorysCatalogProductRecord:
    role: str
    dataset_id: str
    catalog_status: CatalogStatus
    version: str | None
    temporal_start: dt.date | None
    temporal_end: dt.date | None


def _config_date(value: Any) -> dt.date:
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def _ms_to_utc_date(ms: float) -> dt.date:
    return dt.datetime.utcfromtimestamp(ms / 1000.0).date()


def temporal_extent_from_describe(catalogue: Any) -> tuple[dt.date, dt.date, str | None]:
    """
    Extract daily temporal coverage and dataset version label from ``copernicusmarine.describe``.
    """
    products = getattr(catalogue, "products", None) or []
    if not products:
        raise ValueError("describe catalogue has no products")
    datasets = getattr(products[0], "datasets", None) or []
    if not datasets:
        raise ValueError("describe catalogue has no datasets")
    versions = getattr(datasets[0], "versions", None) or []
    if not versions:
        raise ValueError("describe catalogue has no versions")
    version_label = getattr(versions[0], "label", None)
    parts = getattr(versions[0], "parts", None) or []
    t_min: float | None = None
    t_max: float | None = None
    for part in parts:
        for service in getattr(part, "services", None) or []:
            for variable in getattr(service, "variables", None) or []:
                for coord in getattr(variable, "coordinates", None) or []:
                    if getattr(coord, "coordinate_id", None) != "time":
                        continue
                    lo = getattr(coord, "minimum_value", None)
                    hi = getattr(coord, "maximum_value", None)
                    if lo is not None:
                        t_min = lo if t_min is None else min(t_min, lo)
                    if hi is not None:
                        t_max = hi if t_max is None else max(t_max, hi)
    if t_min is None or t_max is None:
        raise ValueError("describe catalogue missing time coordinate extent")
    return _ms_to_utc_date(t_min), _ms_to_utc_date(t_max), str(version_label) if version_label else None


DescribeFn = Callable[[str], Any]


def describe_dataset_record(
    role: str,
    dataset_id: str,
    *,
    describe_fn: DescribeFn,
) -> GlorysCatalogProductRecord:
    try:
        catalogue = describe_fn(dataset_id)
    except Exception as exc:
        msg = str(exc).lower()
        if "dataset not found" in msg or "datasetnotfound" in msg:
            return GlorysCatalogProductRecord(
                role=role,
                dataset_id=dataset_id,
                catalog_status="dataset_not_found",
                version=None,
                temporal_start=None,
                temporal_end=None,
            )
        raise
    start, end, version = temporal_extent_from_describe(catalogue)
    return GlorysCatalogProductRecord(
        role=role,
        dataset_id=dataset_id,
        catalog_status="found",
        version=version,
        temporal_start=start,
        temporal_end=end,
    )


def default_describe_fn(dataset_id: str) -> Any:
    import copernicusmarine

    return copernicusmarine.describe(dataset_id=dataset_id)


def catalog_records_from_config(config: dict[str, Any]) -> list[GlorysCatalogProductRecord]:
    glorys_cfg = config.get("glorys") or {}
    catalog = glorys_cfg.get("catalog") or {}
    preference = list(catalog.get("preference") or ["my", "myint"])
    recorded = catalog.get("products") or {}
    products_cfg = glorys_cfg.get("products") or {}
    out: list[GlorysCatalogProductRecord] = []
    for role in preference:
        meta = recorded.get(role) or {}
        base = products_cfg.get(role) or {}
        dataset_id = str(meta.get("dataset_id") or base.get("id") or "")
        if not dataset_id:
            continue
        status = str(meta.get("catalog_status", "found"))
        if status not in ("found", "dataset_not_found"):
            raise ValueError(f"invalid catalog_status for {role}: {status}")
        temporal_start = meta.get("temporal_start")
        temporal_end = meta.get("temporal_end")
        out.append(
            GlorysCatalogProductRecord(
                role=role,
                dataset_id=dataset_id,
                catalog_status=status,  # type: ignore[arg-type]
                version=meta.get("version"),
                temporal_start=_config_date(temporal_start) if temporal_start else None,
                temporal_end=_config_date(temporal_end) if temporal_end else None,
            )
        )
    if not out:
        raise ValueError("glorys.catalog.products is empty; run catalog refresh against Copernicus Marine")
    return out


def refresh_catalog_into_config(
    config: dict[str, Any],
    *,
    describe_fn: DescribeFn | None = None,
    copernicusmarine_version: str | None = None,
    checked_at: dt.date | None = None,
) -> dict[str, Any]:
    """Call ``describe`` for each configured product and write results under ``glorys.catalog``."""
    describe_fn = describe_fn or default_describe_fn
    glorys_cfg = dict(config.get("glorys") or {})
    catalog = dict(glorys_cfg.get("catalog") or {})
    preference = list(catalog.get("preference") or ["my", "myint"])
    products_cfg = glorys_cfg.get("products") or {}
    product_records: dict[str, Any] = {}
    for role in preference:
        base = products_cfg.get(role) or {}
        dataset_id = str(base.get("id") or "")
        if not dataset_id:
            continue
        rec = describe_dataset_record(role, dataset_id, describe_fn=describe_fn)
        product_records[role] = {
            "dataset_id": rec.dataset_id,
            "catalog_status": rec.catalog_status,
            "version": rec.version,
            "temporal_start": rec.temporal_start.isoformat() if rec.temporal_start else None,
            "temporal_end": rec.temporal_end.isoformat() if rec.temporal_end else None,
        }
    if copernicusmarine_version is None:
        try:
            import copernicusmarine

            copernicusmarine_version = str(copernicusmarine.__version__)
        except Exception:
            copernicusmarine_version = None
    catalog["preference"] = preference
    catalog["copernicusmarine_version"] = copernicusmarine_version
    catalog["checked_at"] = (checked_at or dt.date.today()).isoformat()
    catalog["products"] = product_records
    glorys_cfg["catalog"] = catalog
    out = dict(config)
    out["glorys"] = glorys_cfg
    return out


def glorys_dataset_id_for_calendar_day(
    day: dt.date,
    config: dict[str, Any],
) -> str:
    """
    Return the first preference-ordered catalog product whose live-recorded extent covers ``day``.
    """
    for rec in catalog_records_from_config(config):
        if rec.catalog_status != "found":
            continue
        if rec.temporal_start is None or rec.temporal_end is None:
            continue
        if rec.temporal_start <= day <= rec.temporal_end:
            return rec.dataset_id
    raise GlorysDatasetNotCoveredError(
        day,
        f"no GLORYS catalog product covers {day.isoformat()}",
        reason_code=REASON_GLORYS_DATE_NOT_COVERED,
    )
