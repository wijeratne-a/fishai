"""Explicit policy: ``data/provenance/`` must not change during pytest."""

from __future__ import annotations

from tests.repo_guards import PROVENANCE_DIR, provenance_file_hashes, session_provenance_baseline


def test_data_provenance_directory_is_tracked() -> None:
    assert PROVENANCE_DIR.is_dir()
    baseline = session_provenance_baseline()
    assert baseline, "expected at least one tracked file under data/provenance/"


def test_data_provenance_hashes_match_session_baseline() -> None:
    """Fails mid-session if any test appended to repo pull logs or edited provenance."""
    assert provenance_file_hashes() == session_provenance_baseline()
