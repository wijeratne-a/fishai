#!/usr/bin/env python3
"""Scan all git-tracked text files for credential-like strings and coordinate exposure.

Uses ``git ls-files`` so ``docs/archive/`` and legacy data are included. Skips only
gitignored runtime trees: ``data/raw``, ``data/interim``, ``data/restricted``,
``data/quarantine``, ``data/processed``. Does not print coordinate values.

Coordinate rules live in ``security.coordinate_exposure`` (shared with other CI entrypoints).

Exit 1 on ANY hit in any tracked file.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coordinate_exposure import (
    csv_header_fields,
    header_has_coordinates,
    scan_json_content,
    scan_parquet_path,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

SKIP_PREFIXES = (
    "data/raw/",
    "data/interim/",
    "data/restricted/",
    "data/quarantine/",
    "data/processed/",
    "src/models/tests/fixtures/",
)

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".csv",
    ".tsv",
    ".json",
    ".geojson",
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

CREDENTIAL_PATTERNS = [
    ("aws_access_key_id", re.compile(r"(?i)\bAKIA[0-9A-Z]{16}\b")),
    ("pem_private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    (
        "generic_api_key_assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[=:]\s*['\"][^'\"]{12,}['\"]"
        ),
    ),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9\-_\.]{20,}")),
    ("password_assignment", re.compile(r"(?i)\bpassword\s*[=:]\s*['\"][^'\"]{6,}['\"]")),
]


def git_ls_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=REPO_ROOT, text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]


def should_skip(rel: str) -> bool:
    return any(rel == p.rstrip("/") or rel.startswith(p) for p in SKIP_PREFIXES)


def read_text_limited(path: Path, max_bytes: int = 2_000_000) -> str | None:
    try:
        data = path.read_bytes()[:max_bytes]
    except OSError:
        return None
    if b"\x00" in data[:4096]:
        return None
    return data.decode("utf-8", errors="replace")


def scan_file(rel: str) -> list[str]:
    """Return hit kind strings for a tracked relative path."""
    if should_skip(rel):
        return []
    path = REPO_ROOT / rel
    if not path.is_file():
        return []

    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return scan_parquet_path(path)

    if suffix not in TEXT_SUFFIXES and path.name not in {".env", "Makefile"}:
        return []

    text = read_text_limited(path)
    if text is None:
        return []

    hits: list[str] = []
    for kind, pattern in CREDENTIAL_PATTERNS:
        if pattern.search(text):
            hits.append(f"credential:{kind}")

    if suffix in {".csv", ".tsv"} and not rel.startswith("tests/fixtures/"):
        first = text.splitlines()[0] if text else ""
        delim_fields = csv_header_fields(first.replace("\t", ","))
        if header_has_coordinates(delim_fields):
            hits.append("csv_header:latitude_or_longitude")

    if suffix in {".json", ".geojson"} or rel.endswith(".schema.json"):
        hits.extend(scan_json_content(text, rel=rel))

    return hits


def scan_repository() -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for rel in git_ls_files():
        for kind in scan_file(rel):
            findings.append((kind, rel))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default="",
        help="Optional single file (repo-relative). Default: all git ls-files.",
    )
    args = parser.parse_args(argv)

    if args.path:
        rel = args.path.lstrip("/")
        hits = [(k, rel) for k in scan_file(rel)]
    else:
        hits = scan_repository()

    for kind, rel in hits:
        print(f"HIT\t{kind}\t{rel}")

    if hits:
        print(f"RESULT\tFAIL\thits={len(hits)}", file=sys.stderr)
        return 1

    print("RESULT\tPASS\thits=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
