"""Live Copernicus Marine catalogue resolution for GLORYS dataset ids."""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import requests

from fishai.ingestion.copernicus_compliance import append_pull_log, build_pull_record

CLIENTS_CONFIG_URLS = (
    "https://s3.waw3-1.cloudferro.com/mdl-metadata/clientsConfigV1.json",
    "https://stac.marine.copernicus.eu/clients-config-v1",
)

GLORYS_DATASET_ID = "cmems_mod_glo_phy_my_0.083deg_P1D-m"
GLORYS_CANDIDATE_DATASET_IDS: tuple[str, ...] = (GLORYS_DATASET_ID,)

_REASON_GLORYS_DATASET_NOT_IN_CATALOG = "glorys_dataset_not_in_catalog"
_REASON_GLORYS_DATE_NOT_COVERED = "glorys_date_not_covered"
_REASON_CATALOG_UNREACHABLE = "catalog_unreachable"
_REASON_GLORYS_DATASET_VERSION_CHANGED = "glorys_dataset_version_changed"
_REASON_GLORYS_DATASET_VERSION_NOT_PINNED = "glorys_dataset_version_not_pinned"
_FAILURE_REASON_CODES = frozenset(
    {
        _REASON_GLORYS_DATASET_VERSION_CHANGED,
        _REASON_GLORYS_DATASET_VERSION_NOT_PINNED,
    }
)


class GlorysCatalogError(RuntimeError):
    """Failed to resolve a GLORYS dataset id from the live catalogue."""

    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


@dataclass(frozen=True)
class GlorysCatalogEntry:
    dataset_id: str
    dataset_version: str
    coverage_start: dt.date
    coverage_end: dt.date

    def covers(self, day: dt.date) -> bool:
        return self.coverage_start <= day <= self.coverage_end

    def coverage_dict(self) -> dict[str, str]:
        return {
            "start": self.coverage_start.isoformat(),
            "end": self.coverage_end.isoformat(),
        }


@dataclass(frozen=True)
class GlorysDatasetResolution:
    dataset_id: str
    dataset_version: str
    catalog_coverage: dict[str, str]

    def pull_log_fields(self) -> dict[str, Any]:
        return {
            "dataset_version": self.dataset_version,
            "catalog_coverage": self.catalog_coverage,
            "glorys_catalog_resolution": True,
        }


_catalog_cache: list[GlorysCatalogEntry] | None = None
_catalog_fetch_hook: Callable[[], list[GlorysCatalogEntry]] | None = None


def clear_glorys_catalog_cache() -> None:
    global _catalog_cache
    _catalog_cache = None


def set_catalog_fetch_hook(
    hook: Callable[[], list[GlorysCatalogEntry]] | None,
) -> None:
    global _catalog_fetch_hook, _catalog_cache
    _catalog_fetch_hook = hook
    _catalog_cache = None


def _parse_iso_date(value: str) -> dt.date:
    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    return dt.datetime.fromisoformat(cleaned).date()


def _version_from_stac_item_id(item_id: str, dataset_id: str) -> str:
    prefix = f"{dataset_id}_"
    if item_id.startswith(prefix):
        return item_id[len(prefix) :]
    match = re.search(r"_(\d{6})$", item_id)
    if match:
        return match.group(1)
    return "unknown"


def _stac_item_time_extent(item: dict[str, Any]) -> tuple[dt.date, dt.date]:
    props = item.get("properties") or {}
    start_raw = props.get("start_datetime")
    end_raw = props.get("end_datetime")
    cube = (props.get("cube:dimensions") or {}).get("time") or {}
    extent = cube.get("extent")
    if start_raw is None and extent:
        start_raw, end_raw = extent[0], extent[1]
    if not start_raw or not end_raw:
        raise ValueError("STAC item missing temporal extent")
    return _parse_iso_date(str(start_raw)), _parse_iso_date(str(end_raw))


def _fetch_json(session: requests.Session, url: str) -> dict[str, Any]:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise TypeError(f"expected JSON object from {url}")
    return payload


def _load_clients_config(session: requests.Session) -> dict[str, Any]:
    last_error: Exception | None = None
    for url in CLIENTS_CONFIG_URLS:
        try:
            return _fetch_json(session, url)
        except (requests.RequestException, TypeError, ValueError) as exc:
            last_error = exc
    raise GlorysCatalogError(
        _REASON_CATALOG_UNREACHABLE,
        f"glorys: Copernicus Marine clients config unreachable ({last_error})",
    )


def _describe_dataset_from_catalogue(
    session: requests.Session,
    *,
    root_metadata_url: str,
    id_mapping_url: str,
    dataset_id: str,
) -> GlorysCatalogEntry | None:
    mapping = _fetch_json(session, id_mapping_url)
    product_ids_raw = mapping.get(dataset_id)
    if not product_ids_raw:
        return None
    root = root_metadata_url.rstrip("/")
    for product_id in str(product_ids_raw).split(","):
        product_id = product_id.strip()
        if not product_id:
            continue
        product = _fetch_json(session, f"{root}/{product_id}/product.stac.json")
        for link in product.get("links") or []:
            href = str(link.get("href") or "")
            if link.get("rel") != "item" or dataset_id not in href:
                continue
            item = _fetch_json(session, f"{root}/{product_id}/{href}")
            start, end = _stac_item_time_extent(item)
            version = _version_from_stac_item_id(str(item.get("id") or dataset_id), dataset_id)
            return GlorysCatalogEntry(
                dataset_id=dataset_id,
                dataset_version=version,
                coverage_start=start,
                coverage_end=end,
            )
    return None


def _fetch_catalog_entries_live() -> list[GlorysCatalogEntry]:
    session = requests.Session()
    try:
        clients = _load_clients_config(session)
    except GlorysCatalogError:
        raise
    except (requests.RequestException, TypeError, ValueError, KeyError) as exc:
        raise GlorysCatalogError(
            _REASON_CATALOG_UNREACHABLE,
            f"glorys: Copernicus Marine catalogue unreachable ({exc})",
        ) from exc

    entries: list[GlorysCatalogEntry] = []
    for catalogue in clients.get("catalogues") or []:
        root = str(catalogue.get("stacRoot") or "").rstrip("/")
        id_mapping = catalogue.get("idMapping")
        if not root or not id_mapping:
            continue
        for dataset_id in GLORYS_CANDIDATE_DATASET_IDS:
            try:
                entry = _describe_dataset_from_catalogue(
                    session,
                    root_metadata_url=root,
                    id_mapping_url=str(id_mapping),
                    dataset_id=dataset_id,
                )
            except (requests.RequestException, TypeError, ValueError) as exc:
                raise GlorysCatalogError(
                    _REASON_CATALOG_UNREACHABLE,
                    f"glorys: Copernicus Marine catalogue unreachable ({exc})",
                ) from exc
            if entry is not None:
                entries.append(entry)
    if not entries:
        raise GlorysCatalogError(
            _REASON_GLORYS_DATASET_NOT_IN_CATALOG,
            "glorys: no GLORYS candidate datasets found in the live catalogue",
        )
    return entries


def load_catalog_entries() -> list[GlorysCatalogEntry]:
    """Return cached GLORYS catalogue entries (at most one live fetch per run)."""
    global _catalog_cache
    if _catalog_cache is not None:
        return _catalog_cache
    if _catalog_fetch_hook is not None:
        _catalog_cache = _catalog_fetch_hook()
        if not _catalog_cache:
            raise GlorysCatalogError(
                _REASON_GLORYS_DATASET_NOT_IN_CATALOG,
                "glorys: no GLORYS candidate datasets found in the live catalogue",
            )
        return _catalog_cache
    _catalog_cache = _fetch_catalog_entries_live()
    return _catalog_cache


def _pick_entry_for_date(
    entries: list[GlorysCatalogEntry],
    day: dt.date,
) -> GlorysCatalogEntry:
    covering = [entry for entry in entries if entry.covers(day)]
    if not covering:
        raise GlorysCatalogError(
            _REASON_GLORYS_DATE_NOT_COVERED,
            f"glorys: no live catalogue dataset covers {day}",
        )
    return covering[0]


def resolve_glorys_dataset_for_date(day: dt.date) -> GlorysDatasetResolution:
    """Resolve the Copernicus dataset id whose live coverage contains ``day``."""
    entries = load_catalog_entries()
    entry = _pick_entry_for_date(entries, day)
    return GlorysDatasetResolution(
        dataset_id=entry.dataset_id,
        dataset_version=entry.dataset_version,
        catalog_coverage=entry.coverage_dict(),
    )


def recorded_glorys_dataset_version(
    log_path: Path | None,
    dataset_id: str,
) -> str | None:
    """Return the dataset_version previously logged for ``dataset_id``, if any."""
    if log_path is None or not log_path.is_file():
        return None
    versions: set[str] = set()
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("reason_code") in _FAILURE_REASON_CODES:
            continue
        if record.get("dataset_id") != dataset_id:
            continue
        version = record.get("dataset_version")
        if version is not None:
            versions.add(str(version))
    if not versions:
        return None
    if len(versions) > 1:
        raise GlorysCatalogError(
            _REASON_GLORYS_DATASET_VERSION_CHANGED,
            f"glorys: inconsistent dataset_version values in pull log for {dataset_id!r}",
        )
    return next(iter(versions))


@lru_cache(maxsize=1)
def pinned_glorys_catalog_version() -> str:
    """Pinned GLORYS catalogue version from harmonization pre-registration."""
    from fishai.evaluation.harmonization_prereg import load_harmonization_prereg

    doc = load_harmonization_prereg()
    glorys = doc["harmonization_wcofs_glorys"]["glorys_reference_dataset"]
    return str(glorys["pinned_catalog_version"])


def _append_glorys_version_failure(
    reason_code: str,
    resolution: GlorysDatasetResolution,
    *,
    log_path: Path | None,
    extra: dict[str, Any],
) -> None:
    failure: dict[str, Any] = {
        "reason_code": reason_code,
        "dataset_id": resolution.dataset_id,
        "dataset_version": resolution.dataset_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    failure.update(extra)
    if log_path is not None:
        append_pull_log(failure, log_path=log_path)


def ensure_glorys_dataset_version_allowed(
    resolution: GlorysDatasetResolution,
    *,
    log_path: Path | None,
) -> None:
    """
    Block pulls before fetch when the catalogue version is not allowed.

    On reruns, compare to the version recorded in the pull log. On first run
    (empty log), compare to ``pinned_catalog_version`` in harmonization prereg.
    Appends a failure record with ``reason_code`` only; never appends a pull record.
    """
    recorded = recorded_glorys_dataset_version(log_path, resolution.dataset_id)
    if recorded is not None:
        if recorded == resolution.dataset_version:
            return
        _append_glorys_version_failure(
            _REASON_GLORYS_DATASET_VERSION_CHANGED,
            resolution,
            log_path=log_path,
            extra={"recorded_dataset_version": recorded},
        )
        raise GlorysCatalogError(
            _REASON_GLORYS_DATASET_VERSION_CHANGED,
            (
                f"glorys: catalogue dataset_version {resolution.dataset_version!r} "
                f"differs from recorded {recorded!r} for {resolution.dataset_id!r}"
            ),
        )

    pinned = pinned_glorys_catalog_version()
    if resolution.dataset_version == pinned:
        return
    _append_glorys_version_failure(
        _REASON_GLORYS_DATASET_VERSION_NOT_PINNED,
        resolution,
        log_path=log_path,
        extra={"pinned_catalog_version": pinned},
    )
    raise GlorysCatalogError(
        _REASON_GLORYS_DATASET_VERSION_NOT_PINNED,
        (
            f"glorys: catalogue dataset_version {resolution.dataset_version!r} "
            f"differs from pinned prereg version {pinned!r}"
        ),
    )


def guard_glorys_version_before_fetch(
    day: dt.date,
    *,
    log_path: Path | None,
) -> GlorysDatasetResolution:
    """
    Resolve catalogue metadata and enforce version policy **before** any data fetch.

    Call this from ``fetch_day`` and overlap pairing immediately prior to
    ``fetch_fn`` / ``glorys_fetch``. ``write_glorys_pull_log_record`` does not
    re-run this guard.
    """
    resolution = resolve_glorys_dataset_for_date(day)
    ensure_glorys_dataset_version_allowed(resolution, log_path=log_path)
    return resolution


def write_glorys_pull_log_record(
    day: dt.date,
    resolution: GlorysDatasetResolution,
    *,
    variables: tuple[str, ...] | list[str],
    bbox: tuple[float, float, float, float],
    log_path: Path,
    request_count: int = 1,
) -> dict[str, Any]:
    """Append one successful GLORYS pull log line (call only after fetch succeeds)."""
    record = build_pull_record(
        dataset_id=resolution.dataset_id,
        date_start=day.isoformat(),
        date_end=day.isoformat(),
        variables=variables,
        bbox=bbox,
        request_count=request_count,
    )
    record.update(resolution.pull_log_fields())
    append_pull_log(record, log_path=log_path)
    return record
