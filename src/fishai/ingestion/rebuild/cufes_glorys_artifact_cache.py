"""Durable GHCR-backed cache for CUFES × GLORYS training-table rebuild artifacts."""

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from fishai.ingestion.biology.cufes.fetch import BBox
from fishai.ingestion.biology.cufes.pipeline import pilot_bbox_from_manifest, sync_cufes
from fishai.ingestion.physics.cufes_training_covariates import (
    DEFAULT_DROP_SUMMARY_NAME,
    run_build_cufes_training_covariates,
)
from fishai.ingestion.physics.glorys_catalog import pinned_glorys_catalog_version
from fishai.ingestion.physics.wcofs_glorys_coverage import expected_cufes_counts
from fishai.ingestion.physics.wcofs_glorys_overlap import load_overlap_config
from fishai.ingestion.physics.wcofs_h_glorys_store import (
    _sha256_path,
    load_wcofs_h_glorys_grid,
    load_wcofs_h_manifest,
)
from fishai.ingestion.physics.wind_shared_forcing import UPWELLING_STATUS_NO_CONSISTENT_WIND
from fishai.ingestion.sources import REPO_ROOT

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
MANIFEST_NAME = "cufes_glorys_rebuild_manifest.json"
CODE_PATHS_MANIFEST = WORKSPACE_ROOT / "scripts" / "ci" / "cufes_glorys_rebuild_code_paths.txt"

CUFES_REBUILD_START = date(1996, 3, 15)
CUFES_REBUILD_END = date(2022, 4, 27)
GLORYS_TRAINING_DATASET_ID = "cmems_mod_glo_phy_my_0.083deg_P1D-m"

PROCESSED_ARTIFACTS: tuple[str, ...] = (
    "data/processed/calcofi_cufes/cufes_events.parquet",
    "data/processed/calcofi_cufes/cufes_counts.parquet",
    "data/processed/calcofi_cufes/cufes_training_covariates.parquet",
    "data/processed/calcofi_cufes/cufes_training_covariate_drops.parquet",
    "data/processed/calcofi_cufes/cufes_training_covariate_drop_summary.json",
)


class CufesGlorysRebuildCacheError(RuntimeError):
    """Cache restore, verify, or guard failure."""


def _canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compute_code_version_hash(*, manifest_path: Path | None = None) -> str:
    manifest = manifest_path or CODE_PATHS_MANIFEST
    if not manifest.is_file():
        raise CufesGlorysRebuildCacheError(f"missing code paths manifest: {manifest}")
    digest = hashlib.sha256()
    with manifest.open(encoding="utf-8") as handle:
        for line in handle:
            relpath = line.split("#", 1)[0].strip()
            if not relpath:
                continue
            path = WORKSPACE_ROOT / relpath
            if not path.is_file():
                raise CufesGlorysRebuildCacheError(f"missing builder input: {relpath}")
            digest.update(relpath.encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\n")
    return digest.hexdigest()


def cufes_query_bbox(*, manifest_path: Path | None = None) -> BBox:
    return pilot_bbox_from_manifest(manifest_path)


def cache_key_material(*, code_version: str | None = None) -> dict[str, Any]:
    box = cufes_query_bbox()
    return {
        "cufes_start": CUFES_REBUILD_START.isoformat(),
        "cufes_end": CUFES_REBUILD_END.isoformat(),
        "cufes_bbox": {
            "lat_min": box.lat_min,
            "lat_max": box.lat_max,
            "lon_min": box.lon_min,
            "lon_max": box.lon_max,
        },
        "glorys_dataset_id": GLORYS_TRAINING_DATASET_ID,
        "glorys_catalogue_version": pinned_glorys_catalog_version(),
        "code_version": code_version or compute_code_version_hash(),
    }


def compute_cache_key(*, code_version: str | None = None) -> str:
    material = cache_key_material(code_version=code_version)
    return hashlib.sha256(_canonical_json(material)).hexdigest()


def _rel_paths_for_archive(*, repo_root: Path) -> list[str]:
    paths = list(PROCESSED_ARTIFACTS)
    raw_dir = repo_root / "data" / "raw" / "calcofi_cufes"
    if raw_dir.is_dir():
        for csv in sorted(raw_dir.glob("erdCalCOFIcufes_*.csv")):
            try:
                rel = csv.resolve().relative_to(repo_root.resolve()).as_posix()
            except ValueError:
                rel = csv.as_posix()
            paths.append(rel)
    return paths


def build_archive_manifest(
    *,
    repo_root: Path | None = None,
    cache_key: str | None = None,
) -> dict[str, Any]:
    root = repo_root or REPO_ROOT
    key = cache_key or compute_cache_key()
    files: dict[str, str] = {}
    for rel in _rel_paths_for_archive(repo_root=root):
        path = root / rel
        if not path.is_file():
            raise CufesGlorysRebuildCacheError(f"missing artifact for cache pack: {rel}")
        files[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    missing = [rel for rel in PROCESSED_ARTIFACTS if rel not in files]
    if missing:
        raise CufesGlorysRebuildCacheError(f"processed rebuild outputs missing: {missing}")
    return {
        "schema_version": 1,
        "cache_key": key,
        "cache_key_material": cache_key_material(),
        "files": files,
    }


def write_cache_archive(
    archive_path: Path,
    *,
    repo_root: Path | None = None,
    cache_key: str | None = None,
) -> dict[str, Any]:
    root = repo_root or REPO_ROOT
    manifest = build_archive_manifest(repo_root=root, cache_key=cache_key)
    archive_path = Path(archive_path)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, mode="w:gz") as tar:
        manifest_bytes = _canonical_json(manifest)
        manifest_info = tarfile.TarInfo(name=MANIFEST_NAME)
        manifest_info.size = len(manifest_bytes)
        tar.addfile(manifest_info, fileobj=__import__("io").BytesIO(manifest_bytes))
        for rel in sorted(manifest["files"]):
            tar.add(root / rel, arcname=rel)
    return manifest


def restore_cache_archive(archive_path: Path, *, repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or REPO_ROOT
    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise CufesGlorysRebuildCacheError(f"cache archive missing: {archive_path}")
    with tarfile.open(archive_path, mode="r:gz") as tar:
        manifest_member = tar.getmember(MANIFEST_NAME)
        extracted = tar.extractfile(manifest_member)
        if extracted is None:
            raise CufesGlorysRebuildCacheError("cache archive missing manifest payload")
        manifest = json.loads(extracted.read().decode("utf-8"))
        expected_key = str(manifest.get("cache_key") or "")
        if expected_key != compute_cache_key():
            raise CufesGlorysRebuildCacheError(
                f"cache key mismatch: archive {expected_key}, current {compute_cache_key()}"
            )
        files = manifest.get("files") or {}
        for rel, digest in files.items():
            member = tar.getmember(rel)
            payload = tar.extractfile(member)
            if payload is None:
                raise CufesGlorysRebuildCacheError(f"empty member in cache archive: {rel}")
            data = payload.read()
            actual = hashlib.sha256(data).hexdigest()
            if actual != digest:
                raise CufesGlorysRebuildCacheError(f"sha256 mismatch for {rel}")
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    return manifest


@dataclass(frozen=True)
class RebuildGuardOptions:
    expected_kept_event_count: int | None = None
    verify_wcofs_h_sha256: bool = True


def assert_cufes_glorys_rebuild_guards(
    *,
    repo_root: Path | None = None,
    options: RebuildGuardOptions | None = None,
) -> None:
    """Same post-build checks on cache hit and cold miss (fail closed)."""
    root = repo_root or REPO_ROOT
    opts = options or RebuildGuardOptions()
    cfg = load_overlap_config()
    expected_kept, _reduced = expected_cufes_counts(cfg)
    if opts.expected_kept_event_count is not None:
        expected_kept = int(opts.expected_kept_event_count)

    events_path = root / "data/processed/calcofi_cufes/cufes_events.parquet"
    if not events_path.is_file():
        raise CufesGlorysRebuildCacheError(f"missing events parquet: {events_path}")
    events = pd.read_parquet(events_path)
    kept_n = int(len(events))
    if kept_n != expected_kept:
        raise CufesGlorysRebuildCacheError(
            f"QC-kept event count {kept_n} != expected {expected_kept}"
        )

    summary_path = root / "data/processed/calcofi_cufes" / DEFAULT_DROP_SUMMARY_NAME
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        input_n = int(summary.get("input_event_count", -1))
        if input_n != kept_n:
            raise CufesGlorysRebuildCacheError(
                f"drop summary input_event_count {input_n} != events rows {kept_n}"
            )

    manifest = load_wcofs_h_manifest()
    expected_sha = manifest.get("sha256")
    if opts.verify_wcofs_h_sha256 and expected_sha:
        rel = str(manifest.get("artifact_path") or "")
        artifact = Path(rel) if Path(rel).is_absolute() else root / rel
        actual_sha = _sha256_path(artifact)
        if actual_sha != str(expected_sha):
            raise CufesGlorysRebuildCacheError("WCOFS h grid sha256 mismatch vs manifest")
        load_wcofs_h_glorys_grid(artifact_path=artifact, verify_sha256=True)

    cov_path = root / "data/processed/calcofi_cufes/cufes_training_covariates.parquet"
    if not cov_path.is_file():
        raise CufesGlorysRebuildCacheError(f"missing training covariates: {cov_path}")
    cov = pd.read_parquet(cov_path)
    if "upwelling" not in cov.columns:
        raise CufesGlorysRebuildCacheError("training covariates missing upwelling column")
    if not cov["upwelling"].isna().all():
        raise CufesGlorysRebuildCacheError("upwelling must remain null on all rows after rebuild")
    if "upwelling_status" in cov.columns:
        status = cov["upwelling_status"].astype(str)
        if not (status == UPWELLING_STATUS_NO_CONSISTENT_WIND).all():
            raise CufesGlorysRebuildCacheError("upwelling_status must document no consistent wind product")


def default_cold_rebuild(*, fetch_cufes: bool = True) -> dict[str, Any]:
    """ERDDAP yearly CSV pull + GLORYS subset build (live network; not for hermetic tests)."""
    box = cufes_query_bbox()
    cufes_result = sync_cufes(
        CUFES_REBUILD_START,
        CUFES_REBUILD_END,
        fetch=fetch_cufes,
        bbox=box,
    )
    glorys_result = run_build_cufes_training_covariates()
    return {"cufes": cufes_result, "glorys": glorys_result}


def run_cufes_glorys_rebuild(
    *,
    skip_cache: bool = False,
    publish_cache: bool = False,
    repo_root: Path | None = None,
    archive_path: Path | None = None,
    cold_rebuild_fn: Callable[[], dict[str, Any]] | None = None,
    restore_archive_fn: Callable[[Path], dict[str, Any]] | None = None,
    guard_options: RebuildGuardOptions | None = None,
) -> dict[str, Any]:
    """
    Restore durable cache when present; otherwise run the cold builders once.

    On a cache hit, ERDDAP and Copernicus GLORYS downloads are not invoked; restored
    files pass sha256 verification, then the same post-build guards run.
    """
    root = repo_root or REPO_ROOT
    key = compute_cache_key()
    restore_fn = restore_archive_fn or restore_cache_archive
    cold_fn = cold_rebuild_fn or (lambda: default_cold_rebuild())
    archive = archive_path or (root / "data" / "cache" / f"cufes_glorys_rebuild_{key}.tar.gz")

    if not skip_cache and archive.is_file():
        manifest = restore_fn(archive, repo_root=root)
        assert_cufes_glorys_rebuild_guards(repo_root=root, options=guard_options)
        return {
            "cache_hit": True,
            "cache_key": key,
            "archive_path": str(archive),
            "manifest": manifest,
            "cold_path_ran": False,
        }

    cold_result = cold_fn()
    assert_cufes_glorys_rebuild_guards(repo_root=root, options=guard_options)
    out: dict[str, Any] = {
        "cache_hit": False,
        "cache_key": key,
        "cold_path_ran": True,
        "cold_result": cold_result,
    }
    if publish_cache:
        manifest = write_cache_archive(archive, repo_root=root, cache_key=key)
        out["archive_path"] = str(archive)
        out["manifest"] = manifest
    return out


def extract_docker_cache_image(image: str, *, dest_archive: Path) -> None:
    """Copy ``/artifact.tar.gz`` from a GHCR cache image ref into ``dest_archive``."""
    import subprocess

    dest_archive = Path(dest_archive)
    dest_archive.parent.mkdir(parents=True, exist_ok=True)
    container = subprocess.check_output(
        ["docker", "create", image],
        text=True,
    ).strip()
    try:
        subprocess.check_call(["docker", "cp", f"{container}:/artifact.tar.gz", str(dest_archive)])
    finally:
        subprocess.call(["docker", "rm", container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def publish_cache_archive_to_image(
    archive_path: Path,
    image: str,
    *,
    cache_key: str | None = None,
) -> None:
    """Build and push a labeled GHCR image wrapping ``archive_path`` (requires docker + login)."""
    import subprocess

    key = cache_key or compute_cache_key()
    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise CufesGlorysRebuildCacheError(f"cannot publish missing archive: {archive_path}")
    staging = archive_path.parent / f".docker_staging_{key}"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    shutil.copy2(archive_path, staging / "artifact.tar.gz")
    subprocess.check_call(
        [
            "docker",
            "build",
            "-f",
            str(REPO_ROOT / "docker" / "Dockerfile.cufes-glorys-cache"),
            "--build-arg",
            f"FISHAI_CUFES_GLORYS_CACHE_KEY={key}",
            "-t",
            image,
            str(staging),
        ],
        cwd=str(REPO_ROOT),
    )
    subprocess.check_call(["docker", "push", image])
    shutil.rmtree(staging)
