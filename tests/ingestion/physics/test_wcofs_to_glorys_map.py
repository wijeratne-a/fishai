"""WCOFS-to-GLORYS correction map (synthetic overlap only)."""

from __future__ import annotations

import json
import tempfile

import numpy as np
import pandas as pd

from fishai.ingestion.physics.wcofs_to_glorys_map import (
    HarmonizationMapHashError,
    HarmonizationMapLeakageError,
    MAPPED_VARIABLES,
    apply_map,
    apply_map_to_overlap_frame,
    fit_correction_map_from_overlap,
    load_correction_map,
    sha256_file,
    write_correction_map_artifacts,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config


def _synthetic_overlap_frame(
    n: int = 400,
    *,
    a: float = 1.5,
    b: float = 0.8,
    noise: float = 0.0,
    day: str = "2024-10-01",
) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    nearshore = rng.random(n) < 0.5
    rows: list[dict[str, object]] = []
    for i in range(n):
        x = rng.normal(10.0, 2.0)
        y = a + b * x + rng.normal(0.0, noise)
        row: dict[str, object] = {
            "day": day,
            "split": "fit",
            "nearshore": bool(nearshore[i]),
            "glorys_j": i // 20,
            "glorys_i": i % 20,
        }
        for var in MAPPED_VARIABLES:
            row[f"wcofs_{var}"] = x + rng.normal(0, 0.01)
            row[f"glorys_{var}"] = y + rng.normal(0, 0.01)
        row["wcofs_upwelling"] = 0.12 + i * 1e-6
        rows.append(row)
    return pd.DataFrame(rows)


def test_coefficient_recovery_on_synthetic_overlap() -> None:
    cfg = load_overlap_config()
    df = _synthetic_overlap_frame(n=800, a=2.0, b=1.25, noise=0.0)
    doc = fit_correction_map_from_overlap(df, config=cfg)
    for stratum in ("nearshore", "offshore"):
        c = doc["coefficients"]["T3m"][stratum]
        assert c["n"] >= 50
        assert abs(c["a"] - 2.0) < 0.15
        assert abs(c["b"] - 1.25) < 0.15


def test_leakage_guard_rejects_test_split_rows() -> None:
    cfg = load_overlap_config()
    df = _synthetic_overlap_frame(day="2025-09-15")
    df["split"] = "test"
    try:
        fit_correction_map_from_overlap(df, config=cfg)
    except HarmonizationMapLeakageError:
        return
    raise AssertionError("expected HarmonizationMapLeakageError")


def test_hash_verification_on_load() -> None:
    cfg = load_overlap_config()
    doc = fit_correction_map_from_overlap(_synthetic_overlap_frame(), config=cfg)
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_correction_map_artifacts(doc, tmp)
        loaded = load_correction_map(tmp, verify_hash=True)
        assert loaded["coefficients"]["T3m"]["nearshore"]["n"] == doc["coefficients"]["T3m"][
            "nearshore"
        ]["n"]
        map_path = paths["map"]
        tampered = json.loads(map_path.read_text(encoding="utf-8"))
        tampered["schema_version"] = 99
        map_path.write_text(json.dumps(tampered) + "\n", encoding="utf-8")
        try:
            load_correction_map(tmp, verify_hash=True)
        except HarmonizationMapHashError:
            return
        raise AssertionError("expected HarmonizationMapHashError")


def test_apply_map_idempotent_shape() -> None:
    cfg = load_overlap_config()
    doc = fit_correction_map_from_overlap(_synthetic_overlap_frame(), config=cfg)
    nj, ni = 5, 7
    nearshore = np.zeros((nj, ni), dtype=bool)
    nearshore[0, :] = True
    fields = {var: np.linspace(1.0, 2.0, nj * ni).reshape(nj, ni) for var in MAPPED_VARIABLES}
    fields["upwelling"] = np.full((nj, ni), 0.5)
    mapped = apply_map(fields, nearshore, doc)
    assert mapped["T3m"].shape == fields["T3m"].shape
    again = apply_map(mapped, nearshore, doc)
    assert again["T3m"].shape == mapped["T3m"].shape


def test_apply_map_preserves_missing_values() -> None:
    cfg = load_overlap_config()
    doc = fit_correction_map_from_overlap(_synthetic_overlap_frame(), config=cfg)
    nearshore = np.array([[True, False], [False, True]])
    fields = {var: np.array([[1.0, np.nan], [np.nan, 3.0]]) for var in MAPPED_VARIABLES}
    mapped = apply_map(fields, nearshore, doc)
    assert np.isnan(mapped["T3m"][0, 1])
    assert np.isnan(mapped["T3m"][1, 0])


def test_upwelling_passes_through_unchanged() -> None:
    cfg = load_overlap_config()
    doc = fit_correction_map_from_overlap(_synthetic_overlap_frame(), config=cfg)
    nearshore = np.ones((2, 2), dtype=bool)
    up = np.array([[0.1, 0.2], [0.3, 0.4]])
    fields = {var: np.ones((2, 2)) for var in MAPPED_VARIABLES}
    fields["upwelling"] = up
    mapped = apply_map(fields, nearshore, doc)
    np.testing.assert_array_equal(mapped["upwelling"], up)


def test_apply_map_overlap_frame_columns() -> None:
    cfg = load_overlap_config()
    df = _synthetic_overlap_frame(n=40)
    doc = fit_correction_map_from_overlap(df, config=cfg)
    out = apply_map_to_overlap_frame(df, doc)
    assert "mapped_T3m" in out.columns
    assert out["mapped_upwelling"].equals(out["wcofs_upwelling"])


def test_frozen_repo_map_loads_with_valid_hash() -> None:
    load_correction_map(verify_hash=True)
