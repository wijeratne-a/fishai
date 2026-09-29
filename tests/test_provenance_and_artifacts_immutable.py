"""Document that pytest refuses mutations under ``data/provenance`` and ``artifacts``."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_data_provenance_and_artifacts_immutability_guard_in_conftest() -> None:
    """Enforcement: session autouse ``_provenance_and_artifacts_unchanged_by_tests`` in tests/conftest.py."""
    text = (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert "_provenance_and_artifacts_unchanged_by_tests" in text
    assert "data/provenance" in text
    assert "pytest.fail" in text
