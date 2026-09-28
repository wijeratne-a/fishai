"""WCOFS-to-GLORYS correction map (synthetic overlap only)."""

from __future__ import annotations

import datetime as dt
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from fishai.ingestion.physics.harmonize import glorys_target_grid
from fishai.ingestion.physics.wcofs_to_glorys_map import (
    SYNTHETIC_FIXTURE_DIR,
    HarmonizationMapHashError,
    HarmonizationMapInsufficientDataError,
    HarmonizationMapLeakageError,
    HarmonizationMapSyntheticError,
    MAPPED_VARIABLES,
    apply_map,
    apply_map_to_overlap_frame,
    fit_correction_map_from_overlap,
    load_correction_map,
    write_correction_map_artifacts,
)
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
from tests.ingestion.physics.test_wcofs_glorys_overlap import _synthetic_wcofs


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


def _stratified_overlap_frame(n_per_stratum: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    rows: list[dict[str, object]] = []
    specs = ((True, 1.0, 1.1), (False, 2.0, 0.5))
    for nearshore, a, b in specs:
        for i in range(n_per_stratum):
            x = rng.normal(10.0, 1.5)
            y = a + b * x
            row: dict[str, object] = {
                "day": "2024-10-01",
                "split": "fit",
                "nearshore": nearshore,
                "glorys_j": i // 10,
                "glorys_i": i % 10,
            }
            for var in MAPPED_VARIABLES:
                row[f"wcofs_{var}"] = x
                row[f"glorys_{var}"] = y
            rows.append(row)
    return pd.DataFrame(rows)


def test_coefficient_recovery_on_synthetic_overlap() -> None:
    cfg = load_overlap_config()
    df = _synthetic_overlap_frame(n=800, a=2.0, b=1.25, noise=0.0)
    doc = fit_correction_map_from_overlap(df, config=cfg, synthetic=True)
    for stratum in ("nearshore", "offshore"):
        c = doc["coefficients"]["T3m"][stratum]
        assert c["n"] >= 50
        assert abs(c["a"] - 2.0) < 0.15
        assert abs(c["b"] - 1.25) < 0.15


def test_per_stratum_coefficient_recovery() -> None:
    cfg = load_overlap_config()
    doc = fit_correction_map_from_overlap(_stratified_overlap_frame(), config=cfg, synthetic=True)
    near = doc["coefficients"]["T3m"]["nearshore"]
    off = doc["coefficients"]["T3m"]["offshore"]
    assert abs(near["a"] - 1.0) < 0.1 and abs(near["b"] - 1.1) < 0.1
    assert abs(off["a"] - 2.0) < 0.1 and abs(off["b"] - 0.5) < 0.1


def test_leakage_guard_rejects_test_split_rows() -> None:
    cfg = load_overlap_config()
    df = _synthetic_overlap_frame(day="2025-09-15")
    df["split"] = "test"
    with pytest.raises(HarmonizationMapLeakageError):
        fit_correction_map_from_overlap(df, config=cfg, synthetic=True)


def test_leakage_without_split_column_on_test_day() -> None:
    cfg = load_overlap_config()
    df = _synthetic_overlap_frame(day="2025-09-15")
    df = df.drop(columns=["split"])
    with pytest.raises(HarmonizationMapLeakageError):
        fit_correction_map_from_overlap(df, config=cfg, synthetic=True)


def test_fit_raises_when_stratum_has_insufficient_n() -> None:
    cfg = load_overlap_config()
    df = _stratified_overlap_frame(n_per_stratum=1)
    with pytest.raises(HarmonizationMapInsufficientDataError):
        fit_correction_map_from_overlap(df, config=cfg, synthetic=True)


def test_hash_verification_on_load() -> None:
    cfg = load_overlap_config()
    doc = fit_correction_map_from_overlap(
        _synthetic_overlap_frame(), config=cfg, synthetic=True
    )
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_correction_map_artifacts(doc, tmp)
        loaded = load_correction_map(tmp, verify_hash=True, allow_synthetic=True)
        assert loaded["coefficients"]["T3m"]["nearshore"]["n"] == doc["coefficients"]["T3m"][
            "nearshore"
        ]["n"]
        map_path = paths["map"]
        tampered = json.loads(map_path.read_text(encoding="utf-8"))
        tampered["schema_version"] = 99
        map_path.write_text(json.dumps(tampered) + "\n", encoding="utf-8")
        with pytest.raises(HarmonizationMapHashError):
            load_correction_map(tmp, verify_hash=True, allow_synthetic=True)


def test_synthetic_map_refused_without_allow_flag() -> None:
    with pytest.raises(HarmonizationMapSyntheticError):
        load_correction_map(SYNTHETIC_FIXTURE_DIR, allow_synthetic=False)


def test_synthetic_fixture_loads_with_allow_flag() -> None:
    load_correction_map(SYNTHETIC_FIXTURE_DIR, allow_synthetic=True)


def test_apply_map_idempotent_shape() -> None:
    cfg = load_overlap_config()
    doc = fit_correction_map_from_overlap(
        _synthetic_overlap_frame(), config=cfg, synthetic=True
    )
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
    doc = fit_correction_map_from_overlap(
        _synthetic_overlap_frame(), config=cfg, synthetic=True
    )
    nearshore = np.array([[True, False], [False, True]])
    fields = {var: np.array([[1.0, np.nan], [np.nan, 3.0]]) for var in MAPPED_VARIABLES}
    mapped = apply_map(fields, nearshore, doc)
    assert np.isnan(mapped["T3m"][0, 1])
    assert np.isnan(mapped["T3m"][1, 0])


def test_upwelling_passes_through_unchanged() -> None:
    cfg = load_overlap_config()
    doc = fit_correction_map_from_overlap(
        _synthetic_overlap_frame(), config=cfg, synthetic=True
    )
    nearshore = np.ones((2, 2), dtype=bool)
    up = np.array([[0.1, 0.2], [0.3, 0.4]])
    fields = {var: np.ones((2, 2)) for var in MAPPED_VARIABLES}
    fields["upwelling"] = up
    mapped = apply_map(fields, nearshore, doc)
    np.testing.assert_array_equal(mapped["upwelling"], up)


def test_apply_map_overlap_frame_columns() -> None:
    cfg = load_overlap_config()
    df = _synthetic_overlap_frame(n=40)
    doc = fit_correction_map_from_overlap(df, config=cfg, synthetic=True)
    out = apply_map_to_overlap_frame(df, doc)
    assert "mapped_T3m" in out.columns
    assert out["mapped_upwelling"].equals(out["wcofs_upwelling"])


def test_end_to_end_fit_on_overlap_day_dataframe() -> None:
    from fishai.ingestion.physics.wcofs_glorys_overlap import pair_overlap_from_synthetic

    cfg = load_overlap_config()
    lat_dst, lon_dst = glorys_target_grid(33.0, 33.4, -120.6, -120.1, resolution_deg=0.05)
    z_levels = np.array([0.0, 5.0, 10.0, 50.0])
    nj, ni = len(lat_dst), len(lon_dst)
    nz = z_levels.size
    thetao = 14.0 + 0.12 * z_levels[:, None, None] * np.ones((nz, nj, ni))
    so = np.full((nz, nj, ni), 33.4)
    frame = pair_overlap_from_synthetic(
        dt.date(2024, 9, 10),
        _synthetic_wcofs(),
        thetao,
        so,
        z_levels,
        lat_dst,
        lon_dst,
        config=cfg,
    )
    half = len(frame) // 2
    frame.loc[frame.index[:half], "nearshore"] = True
    frame.loc[frame.index[half:], "nearshore"] = False
    for col in [f"wcofs_{v}" for v in MAPPED_VARIABLES] + [f"glorys_{v}" for v in MAPPED_VARIABLES]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce").fillna(1.0)
    doc = fit_correction_map_from_overlap(frame, config=cfg, synthetic=True)
    assert doc["coefficients"]["T3m"]["nearshore"]["n"] >= 2
