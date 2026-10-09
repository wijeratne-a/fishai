"""FRAM Data Warehouse fetch for groundfish bottom-trawl catch and haul facts."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import quote

from fishai.ingestion.biology.fram_groundfish_trawl.constants import (
    API_BASE,
    CATCH_LAYER,
    CATCH_VARIABLES,
    GROUNDFISH_COMBO_PROJECT,
    HAUL_LAYER,
    HAUL_VARIABLES,
    SCIENTIFIC_NAME_FIELD,
    SOURCE_ID,
    TARGET_SPECIES,
)
from fishai.ingestion.sources import REPO_ROOT, require_approved

DEFAULT_TIMEOUT_SEC = 120.0
DEFAULT_MAX_RETRIES = 5
DEFAULT_BACKOFF_SEC = 2.0


class FramVariableDropError(RuntimeError):
    """Raised when the API silently omits requested selection variables."""


class BBox:
    """Axis-aligned bounding box (degrees)."""

    __slots__ = ("lat_min", "lat_max", "lon_min", "lon_max")

    def __init__(self, lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> None:
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max


def raw_dir() -> Path:
    return REPO_ROOT / "data" / "raw" / "nwfsc_fram_groundfish_trawl"


def build_selection_url(
    layer: str,
    *,
    filters: Sequence[str],
    variables: Sequence[str],
    fmt: str = "json",
) -> str:
    filter_clause = ",".join(filters)
    var_clause = ",".join(variables)
    return (
        f"{API_BASE}/{layer}/selection.{fmt}"
        f"?filters={filter_clause}&variables={var_clause}"
    )


def validate_response_variables(
    rows: list[dict[str, Any]],
    variables: Sequence[str],
    *,
    layer: str,
) -> None:
    """FRAM drops unknown variable names without error; fail closed if keys are missing."""
    if not rows:
        return
    sample = rows[0]
    missing = [name for name in variables if name not in sample]
    if missing:
        raise FramVariableDropError(
            f"{layer}: response missing requested variables (silent API drop): {missing}"
        )


def _http_get_json(url: str, *, timeout: float, max_retries: int, backoff: float) -> list[dict[str, Any]]:
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "fishai-fram-groundfish-ingest/0.1"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            if not isinstance(payload, list):
                raise RuntimeError(f"expected JSON array from FRAM, got {type(payload)!r}")
            return payload
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code == 404:
                return []
            if attempt + 1 < max_retries:
                time.sleep(backoff * (2**attempt))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_err = exc
            if attempt + 1 < max_retries:
                time.sleep(backoff * (2**attempt))
    raise RuntimeError(f"FRAM fetch failed after {max_retries} attempts: {last_err}") from last_err


def iter_survey_years(t0: date, t1: date) -> list[int]:
    if t1 < t0:
        return []
    return list(range(t0.year, t1.year + 1))


def fetch_pelagic_bycatch_catch(
    t0: date,
    t1: date,
    *,
    species: Sequence[str] = TARGET_SPECIES,
    project: str = GROUNDFISH_COMBO_PROJECT,
    dest_dir: Path | None = None,
    timeout: float = DEFAULT_TIMEOUT_SEC,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff: float = DEFAULT_BACKOFF_SEC,
    manifest_path: Path | None = None,
) -> list[Path]:
    """Download tow-level sardine/anchovy catch rows (one JSON file per species-year batch)."""
    require_approved(SOURCE_ID, path=manifest_path)
    out_dir = dest_dir or raw_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for year in iter_survey_years(t0, t1):
        for sp in species:
            filters = [
                f"{SCIENTIFIC_NAME_FIELD}={quote(sp, safe='')}",
                f"date_dim$year={year}",
                f"project={quote(project, safe='')}",
            ]
            url = build_selection_url(CATCH_LAYER, filters=filters, variables=CATCH_VARIABLES)
            rows = _http_get_json(url, timeout=timeout, max_retries=max_retries, backoff=backoff)
            validate_response_variables(rows, CATCH_VARIABLES, layer=CATCH_LAYER)
            slug = sp.replace(" ", "_").lower()
            dest = out_dir / f"catch_{year}_{slug}.json"
            dest.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            written.append(dest)
    return written


def fetch_operation_hauls(
    t0: date,
    t1: date,
    *,
    project: str = GROUNDFISH_COMBO_PROJECT,
    dest_dir: Path | None = None,
    timeout: float = DEFAULT_TIMEOUT_SEC,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff: float = DEFAULT_BACKOFF_SEC,
    manifest_path: Path | None = None,
) -> list[Path]:
    """Download haul effort/position metadata (one JSON file per survey year)."""
    require_approved(SOURCE_ID, path=manifest_path)
    out_dir = dest_dir or raw_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for year in iter_survey_years(t0, t1):
        filters = [f"date_dim$year={year}", f"project={quote(project, safe='')}"]
        url = build_selection_url(HAUL_LAYER, filters=filters, variables=HAUL_VARIABLES)
        rows = _http_get_json(url, timeout=timeout, max_retries=max_retries, backoff=backoff)
        validate_response_variables(rows, HAUL_VARIABLES, layer=HAUL_LAYER)
        dest = out_dir / f"haul_{year}.json"
        dest.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(dest)
    return written


def read_fram_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"expected JSON list in {path}")
    return data


def load_raw_catch_for_window(t0: date, t1: date, raw: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for year in iter_survey_years(t0, t1):
        for path in sorted(raw.glob(f"catch_{year}_*.json")):
            rows.extend(read_fram_json(path))
    return rows


def load_raw_hauls_for_window(t0: date, t1: date, raw: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for year in iter_survey_years(t0, t1):
        path = raw / f"haul_{year}.json"
        if path.is_file():
            rows.extend(read_fram_json(path))
    return rows
