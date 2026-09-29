"""Production GLORYS training build must never stamp Copernicus metadata on synthetic data."""

from __future__ import annotations

import datetime as dt
import os
import site
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from fishai.ingestion.physics.cufes_training_covariates import (
    run_build_cufes_training_covariates,
    write_training_covariates_parquet,
)
from fishai.ingestion.physics.cufes_training_covariates import GlorysFieldStore
from fishai.ingestion.physics.glorys_training_build import (
    COPERNICUS_ENV_VAR_NAMES,
    REASON_CREDENTIALS_MISSING,
    REASON_SYNTHETIC_PROVENANCE_FORBIDDEN,
    REASON_WCOFS_BATHYMETRY_PLACEHOLDER,
    GlorysTrainingBuildError,
    SYNTHETIC_TEST_FIXTURE_SOURCE,
    assert_wcofs_bathymetry_hmin_source,
    assert_wcofs_bathymetry_store,
    is_flat_placeholder_bathymetry,
)
from fishai.ingestion.sources import REPO_ROOT, require_approved
from cufes_glorys_synthetic_fixture import glorys_store_from_synthetic_days


def test_live_build_fails_without_credentials(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for name in COPERNICUS_ENV_VAR_NAMES:
        monkeypatch.delenv(name, raising=False)
    events = pd.DataFrame(
        {
            "event_id": ["e1"],
            "start_time": pd.to_datetime(["2020-06-15T12:00:00Z"], utc=True),
            "stop_time": pd.to_datetime(["2020-06-15T12:10:00Z"], utc=True),
            "start_latitude": [33.0],
            "start_longitude": [-120.0],
            "stop_latitude": [33.01],
            "stop_longitude": [-119.99],
        }
    )
    events_path = tmp_path / "events.parquet"
    events.to_parquet(events_path, index=False)
    with pytest.raises(GlorysTrainingBuildError) as excinfo:
        run_build_cufes_training_covariates(events_path=events_path, output_path=tmp_path / "out.parquet")
    assert excinfo.value.reason_code == REASON_CREDENTIALS_MISSING
    assert not (tmp_path / "out.parquet").exists()


def test_synthetic_fixture_cannot_write_glorys_parquet(tmp_path: Path) -> None:
    store = glorys_store_from_synthetic_days([dt.date(2020, 1, 1)])
    assert store.covariate_data_source == SYNTHETIC_TEST_FIXTURE_SOURCE
    out = pd.DataFrame([{"event_id": "e1", "T3m": 1.0, "excluded": False}])
    with pytest.raises(GlorysTrainingBuildError) as excinfo:
        write_training_covariates_parquet(
            out,
            tmp_path / "bad.parquet",
            entry=require_approved("glorys", purpose="training"),
            store=store,
        )
    assert excinfo.value.reason_code == REASON_SYNTHETIC_PROVENANCE_FORBIDDEN


def test_placeholder_hmin_source_rejected() -> None:
    with pytest.raises(GlorysTrainingBuildError) as excinfo:
        assert_wcofs_bathymetry_hmin_source("placeholder_until_wcofs_h_artifact")
    assert excinfo.value.reason_code == REASON_WCOFS_BATHYMETRY_PLACEHOLDER


def test_flat_500m_bathymetry_is_rejected_even_with_allowed_hmin_label() -> None:
    h = np.full((3, 3), 500.0)
    assert is_flat_placeholder_bathymetry(h)
    store = GlorysFieldStore(
        wcofs_h_m=h,
        has_source=np.ones((3, 3), dtype=bool),
        wet_fraction=np.ones((3, 3)),
        min_wet_fraction=0.5,
        roms_hmin_m=500.0,
        hmin_source="wet_cell_minimum_h",
        lat=np.array([33.0, 33.1, 33.2]),
        lon=np.array([-120.0, -119.9, -119.8]),
        covariate_data_source="copernicus_marine",
    )
    with pytest.raises(GlorysTrainingBuildError) as excinfo:
        assert_wcofs_bathymetry_store(store)
    assert excinfo.value.reason_code == REASON_WCOFS_BATHYMETRY_PLACEHOLDER


def test_live_store_rejects_flat_500m_wcofs_artifact(tmp_path: Path) -> None:
    from fishai.ingestion.physics.cufes_training_covariates import new_glorys_field_store_for_live_build
    from fishai.ingestion.physics.wcofs_h_glorys_store import export_wcofs_h_glorys_grid
    from test_wcofs_h_glorys_store import _mini_wcofs

    artifact = tmp_path / "wcofs_h.zarr"
    manifest = tmp_path / "manifest.json"
    export_wcofs_h_glorys_grid(
        _mini_wcofs(h_value=500.0),
        source_file="tests/flat_500m_placeholder.nc",
        artifact_path=artifact,
        manifest_path=manifest,
    )
    with pytest.raises(GlorysTrainingBuildError) as excinfo:
        new_glorys_field_store_for_live_build(manifest_path=manifest, artifact_path=artifact)
    assert excinfo.value.reason_code == REASON_WCOFS_BATHYMETRY_PLACEHOLDER


def test_synthetic_fixture_default_depth_is_not_flat_500m() -> None:
    store = glorys_store_from_synthetic_days([dt.date(2020, 6, 1)])
    assert not is_flat_placeholder_bathymetry(store.wcofs_h_m)
    assert "placeholder" not in store.hmin_source


def test_production_sources_do_not_embed_500m_placeholder() -> None:
    root = REPO_ROOT / "src" / "fishai"
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "placeholder_until_wcofs_h_artifact" in text:
            offenders.append(f"{path}: placeholder hmin label")
        if "np.full((nj, ni), 500" in text or "np.full((nj, ni), 500.0)" in text:
            offenders.append(f"{path}: flat 500 m fill")
    assert offenders == []


def _credential_env_keys(env: dict[str, str]) -> list[str]:
    blocked: list[str] = []
    for key in env:
        upper = key.upper()
        if key in COPERNICUS_ENV_VAR_NAMES or upper.startswith("COPERNICUS") or upper.startswith("CMEMS"):
            blocked.append(key)
    return blocked


def test_live_build_fails_without_credentials_in_isolated_environment(tmp_path: Path) -> None:
    """Child process with a clean env and empty HOME; host secrets must not leak in."""
    events = pd.DataFrame(
        {
            "event_id": ["e1"],
            "start_time": pd.to_datetime(["2022-03-01T12:00:00Z"], utc=True),
            "stop_time": pd.to_datetime(["2022-03-01T12:10:00Z"], utc=True),
            "start_latitude": [33.0],
            "start_longitude": [-120.0],
            "stop_latitude": [33.01],
            "stop_longitude": [-119.99],
        }
    )
    events_path = tmp_path / "events.parquet"
    events.to_parquet(events_path, index=False)
    out_path = tmp_path / "out.parquet"
    home = tmp_path / "empty-home"
    home.mkdir()
    (home / ".copernicusmarine").mkdir()
    (home / ".copernicusmarine" / "credentials").write_text("not-a-real-secret\n", encoding="utf-8")
    script = tmp_path / "isolated_credential_check.py"
    script.write_text(
        "\n".join(
            [
                "import os",
                "import sys",
                "from pathlib import Path",
                "leaked = [k for k in os.environ if k.upper().startswith('COPERNICUS') or k.upper().startswith('CMEMS')]",
                "if leaked:",
                "    raise SystemExit('leaked:' + ','.join(sorted(leaked)))",
                "from fishai.ingestion.physics.cufes_training_covariates import run_build_cufes_training_covariates",
                "from fishai.ingestion.physics.glorys_training_build import (",
                "    REASON_CREDENTIALS_MISSING,",
                "    GlorysTrainingBuildError,",
                ")",
                f"events_path = Path({str(events_path)!r})",
                f"output_path = Path({str(out_path)!r})",
                "try:",
                "    run_build_cufes_training_covariates(events_path=events_path, output_path=output_path)",
                "except GlorysTrainingBuildError as exc:",
                "    if exc.reason_code != REASON_CREDENTIALS_MISSING:",
                "        raise SystemExit('reason:' + exc.reason_code)",
                "    if output_path.exists():",
                "        raise SystemExit('wrote output')",
                "    raise SystemExit(0)",
                "raise SystemExit('no error')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    env = {k: v for k, v in os.environ.items() if k not in _credential_env_keys(dict(os.environ))}
    env["HOME"] = str(home)
    env["XDG_CONFIG_HOME"] = str(home / "xdg")
    # HOME is empty so credential files are invisible; keep the interpreter's
    # site-packages via absolute PYTHONPATH (user site follows HOME).
    src = str(REPO_ROOT / "src")
    parts = [src, site.getusersitepackages()]
    if env.get("PYTHONPATH"):
        parts.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(parts)
    proc = subprocess.run(
        [sys.executable, str(script)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(tmp_path),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert not out_path.exists()


def test_synthetic_hmin_source_rejected_on_store() -> None:
    store = GlorysFieldStore(
        wcofs_h_m=__import__("numpy").zeros((2, 2)),
        has_source=__import__("numpy").ones((2, 2), dtype=bool),
        wet_fraction=__import__("numpy").ones((2, 2)),
        min_wet_fraction=0.5,
        roms_hmin_m=10.0,
        hmin_source="synthetic_test_fixture",
        lat=__import__("numpy").array([33.0, 33.1]),
        lon=__import__("numpy").array([-120.0, -119.9]),
        covariate_data_source="copernicus_marine",
    )
    with pytest.raises(GlorysTrainingBuildError) as excinfo:
        from fishai.ingestion.physics.glorys_training_build import assert_wcofs_bathymetry_store

        assert_wcofs_bathymetry_store(store)
    assert excinfo.value.reason_code == REASON_WCOFS_BATHYMETRY_PLACEHOLDER
