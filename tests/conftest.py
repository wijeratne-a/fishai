"""Pytest configuration: allow imports of co-located test helpers."""

from __future__ import annotations

import sys
from pathlib import Path

_PHYSICS_TEST_DIR = Path(__file__).resolve().parent / "ingestion" / "physics"
if str(_PHYSICS_TEST_DIR) not in sys.path:
    sys.path.insert(0, str(_PHYSICS_TEST_DIR))
