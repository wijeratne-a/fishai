#!/usr/bin/env python3
"""Build a static egg-encounter map from a schema-valid surface JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fishai.products.static_maps import write_static_map


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a static egg-encounter map")
    parser.add_argument("surface_json", type=Path)
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    rows = json.loads(args.surface_json.read_text(encoding="utf-8"))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_static_map(rows, args.out_dir / "egg_encounter_map.html", args.out_dir / "egg_encounter_cells.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
