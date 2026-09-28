"""Ensure pytest never mutates repo ``data/provenance`` or ``artifacts``."""

from __future__ import annotations

import inspect

import tests.conftest as repo_conftest


def test_session_hook_watches_provenance_and_artifacts() -> None:
    """Actual enforcement: session autouse ``_provenance_and_artifacts_unchanged_by_tests``."""
    src = inspect.getsource(repo_conftest._provenance_and_artifacts_unchanged_by_tests)
    assert "data/provenance" in src
    assert "artifacts" in src
    assert "pytest.fail" in src
    prefixes = [str(p) for p in repo_conftest._TRACKED_PREFIXES]
    assert any("provenance" in p for p in prefixes)
