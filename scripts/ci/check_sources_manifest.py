#!/usr/bin/env python3
"""Ensure every ingestion source module is listed in data/SOURCES.yaml."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
INGESTION = REPO / "src" / "fishai" / "ingestion"
MANIFEST = REPO / "data" / "SOURCES.yaml"


def source_modules() -> list[Path]:
    modules: list[Path] = []
    for sub in ("biology", "physics", "sensors"):
        root = INGESTION / sub
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.py")):
            if path.name == "__init__.py":
                continue
            modules.append(path)
    return modules


def main() -> int:
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    sources = data.get("sources") or {}
    manifest_modules = {
        entry.get("module")
        for entry in sources.values()
        if isinstance(entry, dict) and entry.get("module")
    }
    errors: list[str] = []
    for path in source_modules():
        rel_mod = f"fishai.ingestion.{path.parent.name}.{path.stem}"
        if rel_mod not in manifest_modules:
            errors.append(f"missing_manifest:{rel_mod}")
    for mod in sorted(manifest_modules):
        if mod and mod.startswith("fishai.ingestion."):
            parts = mod.split(".")
            if len(parts) != 4:
                errors.append(f"bad_module_name:{mod}")
                continue
            _, _, sub, stem = parts
            if not (INGESTION / sub / f"{stem}.py").is_file():
                errors.append(f"manifest_without_file:{mod}")
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
