#!/usr/bin/env python3
"""Print glorys_product_for_date(iso_day) for R load_model_data validation."""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from fishai.ingestion.physics.sources.glorys import glorys_product_for_date  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: glorys_product_for_date_cli.py YYYY-MM-DD", file=sys.stderr)
        return 2
    day = dt.date.fromisoformat(sys.argv[1])
    print(glorys_product_for_date(day))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
