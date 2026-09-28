#!/usr/bin/env python3
"""Gate model-eligible files on unit, zero, event-key, and license checks.

Failures are copied to data/quarantine/ without editing data/raw/.
NUM stays a real-valued average. A species is a non-detection only when it is
on that year's list and every length-bin row is zero.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[3]
QUARANTINE = REPO_ROOT / "data" / "quarantine"
LICENSE_MANIFEST = REPO_ROOT / "data" / "manifests" / "source-licenses.csv"

ALLOWED_LICENSE_CLASSES = {
    "AUTO_ACQUIRE_INTERNAL_ONLY",
    "PUBLIC_INTERNAL_USE",
    "OPEN_WITH_CITATION",
    "ICES_PUBLIC_DATRAS",
    "IMOS_AODN_OPEN",
    "OPEN_GOVERNMENT_LICENCE_CANADA",
}

ATLANTIC_EVENT_KEYS = ("PRIMARY_SAMPLE_UNIT", "STATION_NR", "time")
ATLANTIC_NUM = "NUM"
ATLANTIC_CODE = "SPECIES_CD"
ATLANTIC_YEAR = "YEAR"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def open_text(path: Path):
    if path.suffix == ".gz" or path.name.endswith(".csv.gz"):
        return gzip.open(path, "rt", encoding="latin-1", newline="")
    return path.open("rt", encoding="latin-1", newline="")


def looks_like_html(sample: str) -> bool:
    head = sample.lstrip()[:200].lower()
    return head.startswith("<!doctype") or "<html" in head or "<body" in head


def load_license_classes() -> dict[str, str]:
    if not LICENSE_MANIFEST.is_file():
        return {}
    with LICENSE_MANIFEST.open(newline="", encoding="utf-8") as handle:
        return {
            (row.get("dataset_id") or "").strip(): (row.get("access_class") or "").strip()
            for row in csv.DictReader(handle)
        }


def _skip_units_row(row: dict[str, str], year_field: str) -> bool:
    year_s = (row.get(year_field) or "").strip()
    return year_s == ""


def evaluate_atlantic_frame(path: Path) -> dict[str, Any]:
    """Aggregate-only Atlantic RVC checks. Does not emit coordinates."""
    events: dict[tuple[str, str, str], dict[str, Any]] = {}
    zeros = positives = 0
    num_as_int_attempts = 0
    non_numeric = 0
    with open_text(path) as handle:
        reader = csv.DictReader(handle)
        first = True
        for row in reader:
            if first and _skip_units_row(row, ATLANTIC_YEAR):
                first = False
                continue
            first = False
            key = tuple((row.get(k) or "").strip() for k in ATLANTIC_EVENT_KEYS)
            code = (row.get(ATLANTIC_CODE) or "").strip() or "BLANK"
            raw = (row.get(ATLANTIC_NUM) or "").strip()
            try:
                num = float(raw)
            except ValueError:
                non_numeric += 1
                continue
            if raw and "." not in raw and "e" not in raw.lower():
                # Integer-looking strings are allowed as 0/1 averages; flag only
                # when a consumer would cast away a fractional average.
                pass
            if num != int(num):
                # Fractional average present — NUM is not an integer count.
                pass
            else:
                # Integer-valued average is still an average, not a raw count.
                num_as_int_attempts += 0
            if num == 0:
                zeros += 1
                flag = "z"
            elif num > 0:
                positives += 1
                flag = "p"
            else:
                flag = "n"
            rec = events.setdefault(
                key,
                {
                    "codes": set(),
                    "sp": {},
                    "meta": set(),
                },
            )
            rec["codes"].add(code)
            rec["sp"].setdefault(code, {"z": 0, "p": 0})
            rec["sp"][code][flag] = rec["sp"][code].get(flag, 0) + 1
            rec["meta"].add(
                (
                    (row.get("MONTH") or "").strip(),
                    (row.get("DAY") or "").strip(),
                    (row.get("DEPTH") or row.get("SAMPLE_DEPTH") or "").strip(),
                    (row.get("HABITAT_CD") or "").strip(),
                )
            )

    clashes = sum(1 for rec in events.values() if len(rec["meta"]) > 1)
    both = 0
    for rec in events.values():
        for counts in rec["sp"].values():
            if counts.get("z") and counts.get("p"):
                both += 1
    universes = {frozenset(rec["codes"]) for rec in events.values()}
    sizes = [len(rec["codes"]) for rec in events.values()]
    errors: list[str] = []
    if clashes:
        errors.append("EVENT_KEY_UNRESOLVED")
    if zeros == 0:
        errors.append("ZERO_SEMANTICS_UNRESOLVED")
    if len(universes) != 1:
        errors.append("ZERO_SEMANTICS_UNRESOLVED")
    if both:
        errors.append("MIXED_ZERO_AND_POSITIVE_ON_SAME_SPECIES_EVENT")
    if non_numeric:
        errors.append("NUM_NON_NUMERIC")
    status = "MODEL_ELIGIBLE" if not errors else "REJECTED"
    return {
        "events": len(events),
        "zero_rows": zeros,
        "positive_rows": positives,
        "species_list_size": sizes[0] if sizes and min(sizes) == max(sizes) else None,
        "universes": len(universes),
        "metadata_collisions": clashes,
        "species_events_mixed_zero_and_positive": both,
        "num_kept_as_average": True,
        "errors": errors,
        "status": status,
    }


def evaluate_units_sidecar(sidecar: dict[str, Any] | None) -> list[str]:
    """Reject NUM-as-integer-count and other forbidden unit claims."""
    if not sidecar:
        return []
    errors: list[str] = []
    if sidecar.get("treated_as_integer_fish_count") is True:
        errors.append("UC-NUM-AS-INTEGER-COUNT")
    if sidecar.get("measurement_type") == "atlantic_rvc_num" and sidecar.get(
        "treatment"
    ) in {"integer_fish_count", "integer_count"}:
        errors.append("UC-NUM-AS-INTEGER-COUNT")
    if sidecar.get("label_semantics") == "PRESENCE_ONLY_NO_ABSENCE" and sidecar.get(
        "treat_presence_only_as_absence"
    ) is True:
        errors.append("PRESENCE_ONLY_TREATED_AS_ABSENCE")
    return errors


def evaluate_license(dataset_id: str, sidecar: dict[str, Any] | None) -> list[str]:
    classes = load_license_classes()
    declared = ""
    if sidecar:
        declared = (sidecar.get("license_class") or sidecar.get("access_class") or "").strip()
    known = declared or classes.get(dataset_id, "")
    if not known:
        return ["LICENSE_CLASS_UNKNOWN"]
    if known not in ALLOWED_LICENSE_CLASSES:
        return [f"LICENSE_CLASS_NOT_ALLOWED:{known}"]
    return []


def quarantine_copy(path: Path, reason: str) -> Path:
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = QUARANTINE / f"{path.name}.{stamp}.rejected"
    shutil.copy2(path, dest)
    note = dest.with_suffix(dest.suffix + ".json")
    note.write_text(
        json.dumps(
            {
                "source_name": path.name,
                "quarantined_utc": stamp,
                "reason": reason,
                "raw_edited": False,
                "sha256": sha256_file(path),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return dest


def gate_file(
    path: Path,
    *,
    dataset_id: str,
    family: str = "atlantic",
    sidecar: dict[str, Any] | None = None,
    quarantine: bool = True,
) -> dict[str, Any]:
    """Return eligibility. Copies failures to quarantine. Never edits data/raw."""
    result: dict[str, Any] = {
        "path": str(path),
        "dataset_id": dataset_id,
        "family": family,
        "status": "REJECTED",
        "errors": [],
        "quarantine_path": None,
        "raw_edited": False,
        "num_semantics": "real_valued_average",
    }
    errors: list[str] = []
    if not path.is_file():
        errors.append("FILE_NOT_FOUND")
        result["errors"] = errors
        return result

    try:
        with open_text(path) as handle:
            sample = handle.read(4096)
            if looks_like_html(sample):
                errors.append("CONTENT_IS_HTML")
    except OSError:
        errors.append("OPEN_ERROR")
        result["errors"] = errors
        if quarantine:
            result["quarantine_path"] = str(quarantine_copy(path, ";".join(errors)))
        return result

    errors.extend(evaluate_license(dataset_id, sidecar))
    errors.extend(evaluate_units_sidecar(sidecar))

    if family == "atlantic" and "CONTENT_IS_HTML" not in errors:
        frame = evaluate_atlantic_frame(path)
        result["frame"] = {
            k: v
            for k, v in frame.items()
            if k != "errors"
        }
        errors.extend(frame["errors"])
    elif family == "presence_only":
        errors.append("PRESENCE_ONLY_NOT_MODEL_ELIGIBLE_FOR_DETECTION")

    result["errors"] = sorted(set(errors))
    if result["errors"]:
        result["status"] = "REJECTED"
        if quarantine:
            result["quarantine_path"] = str(
                quarantine_copy(path, ";".join(result["errors"]))
            )
    else:
        result["status"] = "MODEL_ELIGIBLE"
    return result


def write_gate_log(results: Iterable[dict[str, Any]], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    rows = list(results)
    fields = [
        "path",
        "dataset_id",
        "family",
        "status",
        "errors",
        "quarantine_path",
        "raw_edited",
    ]
    with dest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for rec in rows:
            writer.writerow(
                {
                    "path": Path(rec["path"]).name,
                    "dataset_id": rec.get("dataset_id", ""),
                    "family": rec.get("family", ""),
                    "status": rec.get("status", ""),
                    "errors": ";".join(rec.get("errors") or []),
                    "quarantine_path": Path(rec["quarantine_path"]).name
                    if rec.get("quarantine_path")
                    else "",
                    "raw_edited": rec.get("raw_edited", False),
                }
            )
