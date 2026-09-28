"""Holdout scorer must not override GLORYS dataset_id on fetch_day."""

from __future__ import annotations

from pathlib import Path

SCORING_PKG = Path(__file__).resolve().parents[3] / "src" / "fishai" / "scoring"


def test_scoring_package_never_passes_dataset_id_to_fetch_day() -> None:
    for path in SCORING_PKG.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "fetch_day" not in text, f"{path} must not call fetch_day"
        assert "dataset_id=" not in text, f"{path} must not pass dataset_id"
