#!/usr/bin/env python3
"""Print FishAI project status from files that exist. Unknown metrics print UNKNOWN."""

from __future__ import annotations

import csv
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSTREAMS = REPO_ROOT / "planning/parallel-workstreams/WORKSTREAMS.yaml"


def read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def count_csv_rows(path: Path) -> int | None:
    if not path.is_file():
        return None
    with path.open(newline="", encoding="utf-8", errors="replace") as fh:
        return sum(1 for _ in csv.DictReader(fh))


def count_validation_failures(path: Path) -> int | None:
    if not path.is_file():
        return None
    failure_tokens = {
        "CORRUPT",
        "WRONG_CONTENT",
        "FAILED",
        "FAIL",
        "INVALID",
        "QUARANTINED",
        "UNSUPPORTED_FORMAT",
    }
    count = 0
    with path.open(newline="", encoding="utf-8", errors="replace") as fh:
        reader = csv.DictReader(fh)
        status_key = None
        if reader.fieldnames:
            for candidate in ("status", "validation_status", "result"):
                if candidate in reader.fieldnames:
                    status_key = candidate
                    break
        if not status_key:
            return None
        for row in reader:
            status = (row.get(status_key) or "").strip().upper()
            if status in failure_tokens or status.startswith("FAIL"):
                count += 1
    return count


def unique_paths_from_manifests() -> tuple[int | None, int | None]:
    manifests = [
        REPO_ROOT / "data/manifests/acquisition-manifest.csv",
        REPO_ROOT / "data/manifests/structured-survey-manifest.csv",
    ]
    paths: set[str] = set()
    sources: set[str] = set()
    any_found = False
    for man in manifests:
        if not man.is_file():
            continue
        any_found = True
        with man.open(newline="", encoding="utf-8", errors="replace") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                p = (row.get("path") or "").strip()
                if p:
                    paths.add(p)
                for key in ("dataset_id", "source_id", "query_url"):
                    v = (row.get(key) or "").strip()
                    if v:
                        sources.add(v)
                        break
    if not any_found:
        return None, None
    return len(sources) or None, len(paths)


def parse_workstream_statuses() -> dict[str, list[str]]:
    text = read_text(WORKSTREAMS)
    buckets: dict[str, list[str]] = {
        "RUNNING": [],
        "BLOCKED": [],
        "PARTIAL": [],
        "READY": [],
        "NOT_STARTED": [],
        "COMPLETE_FOR_CURRENT_CYCLE": [],
        "FAILED": [],
    }
    if not text:
        return buckets
    current_id = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            current_id = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("status:") and current_id:
            status = stripped.split(":", 1)[1].strip()
            buckets.setdefault(status, []).append(current_id)
            current_id = None
    return buckets


def storage_usage() -> str:
    raw = REPO_ROOT / "data/raw"
    if not raw.exists():
        return "UNKNOWN"
    try:
        out = subprocess.check_output(["du", "-sh", str(raw)], text=True)
        return out.split()[0]
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def git_status_summary() -> str:
    try:
        out = subprocess.check_output(
            ["git", "status", "--short"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"
    lines = [ln for ln in out.splitlines() if ln.strip()]
    return f"{len(lines)} paths with local changes" if lines else "clean"


def security_scan_status() -> str:
    scan = REPO_ROOT / "security/precommit_sensitive_scan.py"
    if not scan.is_file():
        return "UNKNOWN"
    result_md = REPO_ROOT / "security/SCAN_RESULT.md"
    if result_md.is_file():
        return "SEE security/SCAN_RESULT.md"
    return "scanner present; no SCAN_RESULT.md leak report"


def backup_status() -> str:
    doc = read_text(REPO_ROOT / "docs/BACKUP_AND_RECOVERY.md")
    if not doc:
        return "UNKNOWN"
    if "NOT_RUN" in doc:
        return "NOT_RUN (no successful restore claimed)"
    return "UNKNOWN"


def project_phase() -> str:
    phase = read_text(REPO_ROOT / "PROJECT_PHASE.md")
    if phase:
        for line in phase.splitlines():
            line = line.strip()
            if line:
                return line[:200]
    return "GLOBAL_DATA_ACQUISITION (inferred; PROJECT_PHASE.md absent)"


def fmt(value) -> str:
    if value is None:
        return "UNKNOWN"
    return str(value)


def main() -> int:
    buckets = parse_workstream_statuses()
    sources, files = unique_paths_from_manifests()
    queue_size = count_csv_rows(REPO_ROOT / "data/manifests/acquisition-queue.csv")
    validation_failures = count_validation_failures(
        REPO_ROOT / "data/manifests/file-validation-results.csv"
    )
    taxonomy_backlog = None
    if (REPO_ROOT / "data/taxonomy/unresolved-names.parquet").is_file():
        taxonomy_backlog = "PRESENT_ROWCOUNT_UNKNOWN"
    unresolved_licenses = count_csv_rows(REPO_ROOT / "data/manifests/source-licenses.csv")
    update_state = REPO_ROOT / "data/manifests/source-update-state.json"
    recent_updates = "present" if update_state.is_file() else "UNKNOWN"

    print(f"PROJECT PHASE: {project_phase()}")
    print(f"RUNNING WORKSTREAMS: {', '.join(buckets.get('RUNNING') or []) or 'NONE'}")
    print(f"BLOCKED WORKSTREAMS: {', '.join(buckets.get('BLOCKED') or []) or 'NONE'}")
    print(f"ACQUISITION QUEUE SIZE: {fmt(queue_size)}")
    print(f"SOURCES ACQUIRED: {fmt(sources)}")
    print(f"FILES ACQUIRED: {fmt(files)}")
    print(f"VALIDATION FAILURES: {fmt(validation_failures)}")
    print(f"TAXONOMY BACKLOG: {fmt(taxonomy_backlog)}")
    print(f"UNRESOLVED LICENSES: {fmt(unresolved_licenses)}")
    print(f"STORAGE USAGE (data/raw): {storage_usage()}")
    print(f"LAST SUCCESSFUL BACKUP: UNKNOWN")
    print(f"BACKUP STATUS: {backup_status()}")
    print(f"RECENT SOURCE UPDATES: {recent_updates}")
    print(f"SECURITY SCAN STATUS: {security_scan_status()}")
    print(f"GIT STATUS: {git_status_summary()}")
    if WORKSTREAMS.is_file():
        partial = ", ".join(buckets.get("PARTIAL") or []) or "NONE"
        ready = ", ".join(buckets.get("READY") or []) or "NONE"
        complete = ", ".join(buckets.get("COMPLETE_FOR_CURRENT_CYCLE") or []) or "NONE"
        print(f"PARTIAL WORKSTREAMS: {partial}")
        print(f"READY WORKSTREAMS: {ready}")
        print(f"COMPLETE_FOR_CURRENT_CYCLE: {complete}")
    else:
        print("WORKSTREAM FILE: UNKNOWN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
