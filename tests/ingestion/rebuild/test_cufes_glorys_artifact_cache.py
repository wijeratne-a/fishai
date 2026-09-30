"""Hermetic tests for the CUFES×GLORYS durable rebuild cache (no ERDDAP / Copernicus I/O)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from fishai.ingestion.rebuild.cufes_glorys_artifact_cache import (
    CufesGlorysRebuildCacheError,
    RebuildGuardOptions,
    build_archive_manifest,
    compute_cache_key,
    restore_cache_archive,
    run_cufes_glorys_rebuild,
    write_cache_archive,
)


def _write_minimal_rebuild_tree(root: Path, *, n_events: int = 4) -> None:
    raw = root / "data" / "raw" / "calcofi_cufes"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "erdCalCOFIcufes_2020.csv").write_text("time,latitude\n", encoding="utf-8")

    proc = root / "data" / "processed" / "calcofi_cufes"
    proc.mkdir(parents=True, exist_ok=True)
    events = pd.DataFrame(
        {
            "event_id": [f"e{i}" for i in range(n_events)],
            "start_time": pd.to_datetime(["2020-06-15T12:00:00Z"] * n_events, utc=True),
            "stop_time": pd.to_datetime(["2020-06-15T12:10:00Z"] * n_events, utc=True),
            "start_latitude": [33.0] * n_events,
            "start_longitude": [-120.0] * n_events,
            "stop_latitude": [33.01] * n_events,
            "stop_longitude": [-119.99] * n_events,
            "pump_readings_used": [1] * n_events,
            "short_event": [False] * n_events,
            "volume_m3": [1.0] * n_events,
        }
    )
    events_path = proc / "cufes_events.parquet"
    events.to_parquet(events_path, index=False)
    counts = pd.DataFrame(
        {"event_id": events["event_id"], "taxon": ["sardine"] * n_events, "count": [1] * n_events}
    )
    counts.to_parquet(proc / "cufes_counts.parquet", index=False)

    cov = pd.DataFrame(
        {
            "event_id": events["event_id"],
            "T3m": [12.0] * n_events,
            "upwelling": [float("nan")] * n_events,
            "upwelling_status": ["no_consistent_wind_product"] * n_events,
            "excluded": [False] * n_events,
        }
    )
    cov.to_parquet(proc / "cufes_training_covariates.parquet", index=False)
    drops = pd.DataFrame({"event_id": [], "reason": []})
    drops.to_parquet(proc / "cufes_training_covariate_drops.parquet", index=False)
    summary = {
        "input_event_count": n_events,
        "kept_event_count": n_events,
        "excluded_event_count": 0,
    }
    (proc / "cufes_training_covariate_drop_summary.json").write_text(
        json.dumps(summary, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def test_cache_key_is_stable_hex() -> None:
    key = compute_cache_key()
    assert len(key) == 64
    assert key == compute_cache_key()


def test_populated_cache_restores_without_cold_path(tmp_path: Path) -> None:
    _write_minimal_rebuild_tree(tmp_path, n_events=4)
    archive = tmp_path / "cache.tar.gz"
    write_cache_archive(archive, repo_root=tmp_path)

    cold_called = {"value": False}

    def _cold() -> dict:
        cold_called["value"] = True
        raise AssertionError("cold rebuild must not run on cache hit")

    # Remove processed files to prove restore repopulates them.
    for path in (tmp_path / "data" / "processed" / "calcofi_cufes").glob("*"):
        path.unlink()

    result = run_cufes_glorys_rebuild(
        repo_root=tmp_path,
        archive_path=archive,
        cold_rebuild_fn=_cold,
        guard_options=RebuildGuardOptions(
            expected_kept_event_count=4,
            verify_wcofs_h_sha256=False,
        ),
    )
    assert result["cache_hit"] is True
    assert result["cold_path_ran"] is False
    assert cold_called["value"] is False
    assert (tmp_path / "data/processed/calcofi_cufes/cufes_training_covariates.parquet").is_file()
    manifest = restore_cache_archive(archive, repo_root=tmp_path)
    assert manifest["cache_key"] == compute_cache_key()


def test_restore_verifies_sha256(tmp_path: Path) -> None:
    _write_minimal_rebuild_tree(tmp_path, n_events=2)
    archive = tmp_path / "cache.tar.gz"
    write_cache_archive(archive, repo_root=tmp_path)

    import tarfile

    tampered = tmp_path / "tampered.tar.gz"
    with tarfile.open(archive, "r:gz") as src, tarfile.open(tampered, "w:gz") as dst:
        for member in src.getmembers():
            data = src.extractfile(member)
            payload = data.read() if data else b""
            if member.name.endswith("cufes_events.parquet"):
                payload = b"not-a-parquet"
            info = tarfile.TarInfo(name=member.name)
            info.size = len(payload)
            dst.addfile(info, fileobj=__import__("io").BytesIO(payload))

    with pytest.raises(CufesGlorysRebuildCacheError, match="sha256 mismatch"):
        restore_cache_archive(tampered, repo_root=tmp_path)


def test_build_archive_manifest_requires_processed_outputs(tmp_path: Path) -> None:
    _write_minimal_rebuild_tree(tmp_path, n_events=1)
    (tmp_path / "data/processed/calcofi_cufes/cufes_training_covariates.parquet").unlink()
    with pytest.raises(CufesGlorysRebuildCacheError, match="missing artifact"):
        build_archive_manifest(repo_root=tmp_path)
