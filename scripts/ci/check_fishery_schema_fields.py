#!/usr/bin/env python3
"""Fail if JSON schema property names or CSV headers use fishery-dependent fields."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

SCHEMA_GLOBS = (
    REPO / "src" / "fishai" / "schemas",
    REPO / "labels",
)

# Field/column name patterns (not cell values or prose).
FORBIDDEN_NAME_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("vessel_id", re.compile(r"(?i)(?:^|[_-])vessel[_-]?id(?:$|[_-])|(?:^|[_-])vesselid(?:$|[_-])")),
    ("permit", re.compile(r"(?i)(?:^|[_-])permit(?:$|[_-]|[_-]id|[_-]number)")),
    ("logbook", re.compile(r"(?i)logbook")),
    ("fishery_observer", re.compile(r"(?i)(?:^|[_-])observer(?:$|[_-]|[_-]id|[_-]program)")),
    ("vms", re.compile(r"(?i)(?:^|[_-])vms(?:$|[_-])|(?:^|[_-])vessel[_-]monitoring")),
    ("landings", re.compile(r"(?i)(?:^|[_-])landings(?:$|[_-])|(?:^|[_-])landing[_-](?:count|weight|qty|volume)")),
]


def git_ls_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=REPO, text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]


def iter_schema_files() -> list[Path]:
    files: list[Path] = []
    for root in SCHEMA_GLOBS:
        if not root.is_dir():
            continue
        files.extend(sorted(root.rglob("*.schema.json")))
        files.extend(sorted(root.glob("*.json")))
    # De-dupe
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in files:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def iter_tracked_csv_headers() -> list[tuple[str, list[str]]]:
    headers: list[tuple[str, list[str]]] = []
    for rel in git_ls_files():
        if not rel.lower().endswith(".csv"):
            continue
        path = REPO / rel
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                row = next(csv.reader(handle), None)
        except OSError:
            continue
        if row:
            headers.append((rel, [cell.strip() for cell in row]))
    return headers


def walk_json_keys(node: object, prefix: str = "") -> list[str]:
    keys: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            keys.append(path)
            keys.extend(walk_json_keys(value, path))
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            keys.extend(walk_json_keys(item, f"{prefix}[{idx}]"))
    return keys


def forbidden_in_name(name: str) -> list[str]:
    normalized = name.replace(" ", "_").replace(".", "_")
    hits: list[str] = []
    for label, pattern in FORBIDDEN_NAME_PATTERNS:
        if pattern.search(normalized):
            hits.append(label)
    return hits


def check_schema_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"unreadable:{path.relative_to(REPO)}:{exc}"]
    for key_path in walk_json_keys(data):
        leaf = key_path.split(".")[-1].split("[")[0]
        for label in forbidden_in_name(leaf):
            errors.append(f"{path.relative_to(REPO)}:json_key:{leaf}:{label}")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in iter_schema_files():
        errors.extend(check_schema_file(path))

    for rel, header in iter_tracked_csv_headers():
        for col in header:
            for label in forbidden_in_name(col):
                errors.append(f"{rel}:csv_column:{col}:{label}")

    if errors:
        for err in sorted(set(errors)):
            print(err, file=sys.stderr)
        print(f"RESULT FAIL count={len(errors)}", file=sys.stderr)
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
