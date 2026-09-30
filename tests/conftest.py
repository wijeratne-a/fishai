"""Shared pytest hooks (provenance / artifacts immutability)."""

from __future__ import annotations

import hashlib
import ipaddress
import os
import socket
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
_TRACKED_PREFIXES = (
    REPO_ROOT / "data" / "provenance",
    REPO_ROOT / "artifacts",
)

_PHYSICS_TEST_DIR = Path(__file__).resolve().parent / "ingestion" / "physics"
if str(_PHYSICS_TEST_DIR) not in sys.path:
    sys.path.insert(0, str(_PHYSICS_TEST_DIR))


def _tracked_repo_files() -> dict[Path, str]:
    out: dict[Path, str] = {}
    for base in _TRACKED_PREFIXES:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file():
                rel = path.relative_to(REPO_ROOT)
                out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def _tree_snapshot(root: Path) -> dict[str, tuple[int, int]]:
    if not root.is_dir():
        return {}
    return {
        str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }


@pytest.fixture(autouse=True)
def _default_wind_pull_log_not_in_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Training table build records wind status; keep that out of data/provenance in tests."""
    import fishai.ingestion.physics.cufes_training_covariates as ctc

    default_log = tmp_path / "wind_pull_log.jsonl"
    original = ctc.record_upwelling_wind_status_pull_log

    def _redirect(*, log_path: Path | None = None) -> Path:
        return original(log_path=log_path or default_log)

    monkeypatch.setattr(ctc, "record_upwelling_wind_status_pull_log", _redirect)


@pytest.fixture(scope="session", autouse=True)
def _offline_glorys_catalog_fixture() -> None:
    """In-process tests use the committed catalogue fixture unless a hook overrides it."""
    fixture = REPO_ROOT / "src" / "models" / "tests" / "fixtures" / "glorys_pinned_catalog.json"
    os.environ["FISHAI_GLORYS_PINNED_CATALOG_JSON"] = str(fixture)
    from fishai.ingestion.physics.glorys_catalog import clear_glorys_catalog_cache

    clear_glorys_catalog_cache()
    yield
    os.environ.pop("FISHAI_GLORYS_PINNED_CATALOG_JSON", None)


def _is_loopback_host(host: object) -> bool:
    if isinstance(host, bytes):
        host = host.decode(errors="ignore")
    if not isinstance(host, str):
        return False
    if host in ("localhost", "localhost.localdomain"):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class LiveNetworkBlocked(RuntimeError):
    """Raised when a unit test tries to reach a non-loopback host."""


@pytest.fixture(autouse=True)
def _block_live_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests are hermetic: any non-loopback connection or DNS lookup fails at once."""
    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex
    real_getaddrinfo = socket.getaddrinfo

    def _refuse(target: object) -> LiveNetworkBlocked:
        return LiveNetworkBlocked(f"live network access blocked in unit tests: {target!r}")

    def _addr_host(address: object) -> object:
        return address[0] if isinstance(address, tuple) and address else address

    def guarded_connect(self: socket.socket, address: object) -> None:
        if self.family in (socket.AF_INET, socket.AF_INET6) and not _is_loopback_host(_addr_host(address)):
            raise _refuse(address)
        return real_connect(self, address)

    def guarded_connect_ex(self: socket.socket, address: object) -> int:
        if self.family in (socket.AF_INET, socket.AF_INET6) and not _is_loopback_host(_addr_host(address)):
            raise _refuse(address)
        return real_connect_ex(self, address)

    def guarded_getaddrinfo(host: object, *args: object, **kwargs: object):
        if not _is_loopback_host(host):
            raise _refuse(host)
        return real_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)


@pytest.fixture(scope="session", autouse=True)
def _provenance_and_artifacts_unchanged_by_tests() -> None:
    before = _tracked_repo_files()
    yield
    after = _tracked_repo_files()
    if before.keys() != after.keys():
        added = set(after) - set(before)
        removed = set(before) - set(after)
        msg = []
        if added:
            msg.append("new files: " + ", ".join(str(p) for p in sorted(added)))
        if removed:
            msg.append("removed files: " + ", ".join(str(p) for p in sorted(removed)))
        pytest.fail("data/provenance or artifacts tree changed during tests: " + "; ".join(msg))
    changed = [rel for rel in before if before[rel] != after[rel]]
    if changed:
        pytest.fail(
            "data/provenance or artifacts file content changed during tests: "
            + ", ".join(str(p) for p in sorted(changed))
        )


@pytest.fixture
def repo_provenance_snapshot() -> dict[str, tuple[int, int]]:
    """Snapshot of committed provenance files for per-test assertions."""
    root = REPO_ROOT / "data" / "provenance"
    return _tree_snapshot(root)
