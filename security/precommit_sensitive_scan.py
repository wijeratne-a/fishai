#!/usr/bin/env python3
"""Scan tracked trees for credential-like strings and lat/lon CSV headers.

Skips data/raw, data/interim, and data/restricted. Does not print coordinate values.
Exit 1 when hits occur under scannable trees:
  audit, scripts, docs, data/manifests, data/processed, data/metadata
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "coverage",
}

PROTECTED_PREFIXES = (
    "data/raw",
    "data/processed",
    "data/interim",
    "data/restricted",
    "data/quarantine",
    "docs/archive",
)

SCANNABLE_PREFIXES = (
    "src",
    "tests",
    "security",
    "labels",
    "science",
    "scripts",
    "docs",
    "data/manifests",
    "data/metadata",
)

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".csv",
    ".tsv",
    ".json",
    ".yaml",
    ".yml",
    ".env",
    ".toml",
    ".ini",
    ".cfg",
    ".sh",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".sql",
    ".xml",
}

# Patterns that suggest secrets (matched on text; values are not printed).
CREDENTIAL_PATTERNS = [
    ("aws_access_key_id", re.compile(r"(?i)\bAKIA[0-9A-Z]{16}\b")),
    ("pem_private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("generic_api_key_assignment", re.compile(r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[=:]\s*['\"][^'\"]{12,}['\"]")),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9\-_\.]{20,}")),
    ("password_assignment", re.compile(r"(?i)\bpassword\s*[=:]\s*['\"][^'\"]{6,}['\"]")),
]

# Exact header names only (case-insensitive). Do not match metadata flags
# such as has_latitude_header.
COORD_HEADER_NAMES = {
    "latitude",
    "longitude",
    "lat",
    "lon",
    "lng",
    "decimal_latitude",
    "decimal_longitude",
    "decimallatitude",
    "decimallongitude",
    "lat_dd",
    "lon_dd",
}


def rel_posix(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def is_under_prefix(rel: str, prefixes: tuple[str, ...]) -> bool:
    return any(rel == p or rel.startswith(p + "/") for p in prefixes)


def is_protected(rel: str) -> bool:
    return is_under_prefix(rel, PROTECTED_PREFIXES)


def is_scannable(rel: str) -> bool:
    return is_under_prefix(rel, SCANNABLE_PREFIXES)


def should_skip_dir(path: Path) -> bool:
    return path.name in SKIP_DIR_NAMES


def iter_files(root: Path):
    root = root.resolve()
    if root.is_file():
        yield root
        return
    for dirpath, dirnames, filenames in os_walk_safe(root):
        # prune protected and skip dirs in-place
        kept = []
        for name in dirnames:
            child = Path(dirpath) / name
            rel = rel_posix(child, REPO_ROOT)
            if should_skip_dir(child) or is_protected(rel):
                continue
            kept.append(name)
        dirnames[:] = kept
        for name in filenames:
            yield Path(dirpath) / name


def os_walk_safe(root: Path):
    import os

    return os.walk(root)


def read_text_limited(path: Path, max_bytes: int = 2_000_000) -> str | None:
    try:
        data = path.read_bytes()[:max_bytes]
    except OSError:
        return None
    if b"\x00" in data[:4096]:
        return None
    return data.decode("utf-8", errors="replace")


def csv_header_fields(first_line: str) -> list[str]:
    # Lightweight header split; sufficient for exposure screening.
    return [h.strip().strip('"').strip("'").lower() for h in first_line.strip().split(",")]


def header_has_coordinates(fields: list[str]) -> bool:
    for field in fields:
        normalized = field.replace(" ", "_")
        if normalized in COORD_HEADER_NAMES:
            return True
    return False


def scan_file(path: Path, root: Path) -> list[tuple[str, str]]:
    """Return list of (hit_kind, relative_path). Never includes coordinate values."""
    rel = rel_posix(path, root if root.is_dir() else REPO_ROOT)
    # Always resolve relative to repo for policy trees
    rel_repo = rel_posix(path, REPO_ROOT)
    if is_protected(rel_repo):
        return []

    hits: list[tuple[str, str]] = []
    suffix = path.suffix.lower()
    if suffix not in TEXT_SUFFIXES and path.name not in {".env", "Makefile"}:
        return hits

    text = read_text_limited(path)
    if text is None:
        return hits

    for kind, pattern in CREDENTIAL_PATTERNS:
        if pattern.search(text):
            hits.append((f"credential:{kind}", rel_repo))

    if suffix in {".csv", ".tsv"}:
        first = text.splitlines()[0] if text else ""
        delim_fields = csv_header_fields(first.replace("\t", ","))
        if header_has_coordinates(delim_fields):
            hits.append(("csv_header:latitude_or_longitude", rel_repo))

    return hits


def scan_path(target: Path) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Returns (scannable_hits, other_hits)."""
    scannable: list[tuple[str, str]] = []
    other: list[tuple[str, str]] = []
    root = target if target.is_dir() else target.parent
    for path in iter_files(target):
        if not path.is_file():
            continue
        for kind, rel in scan_file(path, root):
            if is_scannable(rel):
                scannable.append((kind, rel))
            else:
                other.append((kind, rel))
    return scannable, other


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default=str(REPO_ROOT),
        help="File or directory to scan (default: repository root)",
    )
    args = parser.parse_args(argv)
    target = Path(args.path).resolve()
    if not target.exists():
        print(f"path_missing: {target}", file=sys.stderr)
        return 2

    scannable_hits, other_hits = scan_path(target)

    # Report file paths and hit kinds only — never coordinate values.
    for kind, rel in scannable_hits + other_hits:
        print(f"HIT\t{kind}\t{rel}")

    if scannable_hits:
        print(f"RESULT\tFAIL\tscannable_hits={len(scannable_hits)}")
        return 1

    print(f"RESULT\tPASS\tscannable_hits=0\tother_hits={len(other_hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
