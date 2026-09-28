"""GLORYS licence, purpose gating, pull log, and attribution guards."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import numpy as np
import pytest

from fishai.ingestion.copernicus_compliance import (
    GLORYS_CREDIT_TEXT,
    GLORYS_DOI,
    GlorysAttributionError,
    append_pull_log,
    build_pull_record,
    require_glorys_attribution,
)
from fishai.ingestion.physics.sources.glorys import (
    PRODUCT_ID,
    fetch_day,
    glorys_column_features,
)
from fishai.ingestion.physics.vertical import (
    CUFES_SAMPLE_DEPTH_M,
    interp_at_depth_from_wcofs_column,
    interp_at_depth_from_z_levels,
)
from fishai.ingestion.sources import SourceNotApprovedError, require_approved


def test_glorys_approved_for_training() -> None:
    entry = require_approved("glorys", purpose="training")
    assert entry["enabled"] is True
    assert GLORYS_CREDIT_TEXT in entry["attribution"]
    assert GLORYS_DOI in entry["attribution"]
    assert entry["attribution"].count(GLORYS_CREDIT_TEXT) == 1


def test_glorys_refused_for_daily_inference() -> None:
    with pytest.raises(SourceNotApprovedError):
        require_approved("glorys", purpose="daily_inference")


def test_glorys_fetch_appends_pull_log(tmp_path: Path) -> None:
    log_path = tmp_path / "copernicus_pull_log.jsonl"
    bbox = (32.0, 35.0, -121.0, -117.0)

    def fake_fetch() -> dict:
        return {"variables": ["thetao"]}

    fetch_day(
        dt.date(2020, 6, 1),
        bbox,
        purpose="hindcast",
        fetch_fn=fake_fetch,
        log_path=log_path,
    )
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["dataset_id"] == PRODUCT_ID
    assert rec["variables"]
    assert rec["request_count"] == 1
    assert "timestamp" in rec


def test_glorys_attribution_guard_requires_credit_and_doi() -> None:
    require_glorys_attribution(
        {
            "glorys_derived": True,
            "attribution": (
                "Generated using E.U. Copernicus Marine Service Information; "
                "https://doi.org/10.48670/moi-00021"
            ),
        }
    )
    with pytest.raises(GlorysAttributionError):
        require_glorys_attribution({"glorys_derived": True, "attribution": "missing"})


def test_interp_3m_glorys_and_wcofs_agree_on_linear_profile() -> None:
    z_levels = np.array([2.6, 3.8, 5.0])
    temp = 16.0 + 0.5 * z_levels
    salt = 33.0 + 0.01 * z_levels
    t_glorys = interp_at_depth_from_z_levels(z_levels, temp, CUFES_SAMPLE_DEPTH_M)
    s_glorys = interp_at_depth_from_z_levels(z_levels, salt, CUFES_SAMPLE_DEPTH_M)

    n = 40
    s_rho = (np.arange(1, n + 1) - n - 0.5) / n
    from fishai.ingestion.physics.vertical import cs_r_vstretching4, s_to_z

    cs_r = cs_r_vstretching4(s_rho, 8.0, 3.0)
    h, zeta = 200.0, 0.0
    z_col = s_to_z(np.array([[h]]), np.array([[zeta]]), s_rho, 50.0, cs_r=cs_r)[:, 0, 0]
    depth = -z_col
    temp_wc = 16.0 + 0.5 * depth
    salt_wc = 33.0 + 0.01 * depth
    t_wc = interp_at_depth_from_wcofs_column(
        h, zeta, s_rho, 50.0, temp_wc, cs_r=cs_r, depth_m=CUFES_SAMPLE_DEPTH_M
    )
    s_wc = interp_at_depth_from_wcofs_column(
        h, zeta, s_rho, 50.0, salt_wc, cs_r=cs_r, depth_m=CUFES_SAMPLE_DEPTH_M
    )
    assert abs(t_glorys - t_wc) < 1e-6
    assert abs(s_glorys - s_wc) < 1e-6
    assert abs(t_glorys - (16.0 + 0.5 * 3.0)) < 1e-6


def test_glorys_mld_computed_mlotst_crosscheck_only() -> None:
    # Depths positive down (GLORYS z-levels); temperature surface-warm.
    z_levels = np.array([50.0, 20.0, 10.0, 5.0, 0.0])
    temp = np.array([10.0, 15.0, 17.8, 17.9, 18.0])
    salt = np.full_like(temp, 33.5)
    feats = glorys_column_features(z_levels, temp, salt, mlotst_native=12.0)
    assert np.isfinite(feats["MLD_m"])
    assert feats["mlotst_crosscheck"] == 12.0
    assert "mlotst" not in feats


def test_pull_log_append_only(tmp_path: Path) -> None:
    log_path = tmp_path / "log.jsonl"
    rec = build_pull_record(
        dataset_id="test",
        date_start="2020-01-01",
        date_end="2020-01-01",
        variables=("thetao",),
        bbox=(1.0, 2.0, -3.0, -4.0),
    )
    append_pull_log(rec, log_path=log_path)
    append_pull_log(rec, log_path=log_path)
    assert len(log_path.read_text(encoding="utf-8").strip().splitlines()) == 2
