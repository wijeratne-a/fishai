"""Scoring package must not read valid time from columns other than ocean_time."""

from __future__ import annotations

import re
from pathlib import Path

HARMONIZATION_SCORING = (
    Path(__file__).resolve().parents[3] / "src" / "fishai" / "scoring" / "harmonization"
)

ALLOWLIST_FILES = frozenset({"wcofs_ocean_time.py", "forecast_age.py"})


def test_scoring_modules_do_not_read_valid_time_except_ocean_time() -> None:
    forbidden_patterns = [
        re.compile(r'\[["\']valid_time["\']\]'),
        re.compile(r'\.valid_time\b'),
        re.compile(r'int\s*\(\s*lead'),
        re.compile(r'lead\s*\[\s*1\s*:\s*\]'),
        re.compile(r'run_time\s*\+\s*\(.*lead'),
        re.compile(r'lead\s*-\s*3'),
    ]
    for path in sorted(HARMONIZATION_SCORING.rglob("*.py")):
        if path.name in ALLOWLIST_FILES:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            match = pattern.search(text)
            assert match is None, f"{path.name} must not derive valid time from lead/tags: {match}"
