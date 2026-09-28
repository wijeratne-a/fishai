#!/usr/bin/env python3
"""Ensure every ingestion source module is listed in data/SOURCES.yaml with required fields."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
INGESTION = REPO / "src" / "fishai" / "ingestion"
MANIFEST = REPO / "data" / "SOURCES.yaml"

REQUIRED_FIELDS = (
    "module",
    "license",
    "license_url",
    "attribution",
    "status",
    "enabled",
)

ALLOWED_STATUS = frozenset({"approved", "pending", "account_required", "disabled"})


def module_path_from_file(path: Path) -> str:
    rel = path.relative_to(INGESTION).with_suffix("")
    return "fishai.ingestion." + ".".join(rel.parts)


def module_path_to_file(mod: str) -> Path | None:
    if not mod.startswith("fishai.ingestion."):
        return None
    parts = mod.split(".")
    if len(parts) < 4:
        return None
    return INGESTION.joinpath(*parts[2:]).with_suffix(".py")


def source_modules() -> list[Path]:
    modules: list[Path] = []
    for sub in ("biology", "sensors"):
        root = INGESTION / sub
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.py")):
            if path.name == "__init__.py":
                continue
            modules.append(path)
    physics_sources = INGESTION / "physics" / "sources"
    if physics_sources.is_dir():
        for path in sorted(physics_sources.glob("*.py")):
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
    for source_id, entry in sources.items():
        if not isinstance(entry, dict):
            errors.append(f"bad_entry:{source_id}")
            continue
        for field in REQUIRED_FIELDS:
            if field not in entry:
                errors.append(f"missing_field:{source_id}:{field}")
        status = entry.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(f"bad_status:{source_id}:{status}")
        if entry.get("enabled") is True and status != "approved":
            errors.append(f"enabled_requires_approved:{source_id}")
        if entry.get("enabled") is True:
            attr = entry.get("attribution")
            if not attr or not str(attr).strip():
                errors.append(f"missing_attribution:{source_id}")
    for path in source_modules():
        rel_mod = module_path_from_file(path)
        if rel_mod not in manifest_modules:
            errors.append(f"missing_manifest:{rel_mod}")
    for mod in sorted(manifest_modules):
        if mod and mod.startswith("fishai.ingestion."):
            file_path = module_path_to_file(mod)
            if file_path is None:
                errors.append(f"bad_module_name:{mod}")
                continue
            if not file_path.is_file():
                errors.append(f"manifest_without_file:{mod}")
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
