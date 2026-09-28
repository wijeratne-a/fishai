"""HTTP client with per-host concurrency limits, backoff, and disk cache."""

from __future__ import annotations

import hashlib
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import requests

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CACHE_ROOT = REPO_ROOT / "data" / "interim" / "physics_cache"

RETRY_STATUS = frozenset({429, 500, 502, 503, 504})
MAX_CONCURRENT_PER_HOST = 2
_CONNECT_TIMEOUT = 15
_READ_TIMEOUT = 120


class _HostLimiter:
    def __init__(self, max_active: int) -> None:
        self._max = max_active
        self._active = 0
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)

    def acquire(self) -> None:
        with self._cond:
            while self._active >= self._max:
                self._cond.wait()
            self._active += 1

    def release(self) -> None:
        with self._cond:
            self._active = max(0, self._active - 1)
            self._cond.notify()

    def halve_limit(self) -> None:
        with self._lock:
            self._max = max(1, self._max // 2)


_host_limiters: dict[str, _HostLimiter] = defaultdict(lambda: _HostLimiter(MAX_CONCURRENT_PER_HOST))


def _cache_key(url: str, extra: str = "") -> str:
    digest = hashlib.sha1(f"{url}|{extra}".encode()).hexdigest()
    return digest


def cache_path(url: str, cache_root: Path | None = None, extra: str = "") -> Path:
    root = cache_root or DEFAULT_CACHE_ROOT
    return root / _cache_key(url, extra)


def get_bytes(
    url: str,
    *,
    cache_root: Path | None = None,
    session: requests.Session | None = None,
    max_attempts: int = 6,
    t0: float = 5.0,
    t_max: float = 300.0,
    use_cache: bool = True,
    extra_cache_key: str = "",
) -> bytes:
    """GET URL with cache, per-host concurrency cap, and exponential backoff."""
    path = cache_path(url, cache_root, extra_cache_key)
    if use_cache and path.is_file():
        return path.read_bytes()

    host = urlparse(url).netloc or "default"
    limiter = _host_limiters[host]
    sess = session or requests.Session()
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        limiter.acquire()
        try:
            resp = sess.get(url, timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT))
            if resp.status_code == 200:
                data = resp.content
                if use_cache:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                return data
            if resp.status_code in RETRY_STATUS:
                if resp.status_code == 429:
                    limiter.halve_limit()
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        time.sleep(min(float(retry_after), t_max))
                raise IOError(f"HTTP {resp.status_code}")
            resp.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            wait = min(t_max, t0 * (2 ** attempt))
            time.sleep(wait)
        finally:
            limiter.release()
    raise RuntimeError(f"GET failed after {max_attempts} attempts: {url}") from last_exc


def head_ok(url: str, *, session: requests.Session | None = None) -> bool:
    return head_metadata(url, session=session).get("status") == 200


def head_metadata(url: str, *, session: requests.Session | None = None) -> dict[str, Any]:
    """HEAD request returning status, ETag, and Content-Length when present."""
    host = urlparse(url).netloc or "default"
    limiter = _host_limiters[host]
    sess = session or requests.Session()
    limiter.acquire()
    try:
        resp = sess.head(url, timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT))
        etag = resp.headers.get("ETag", "").strip('"')
        length = resp.headers.get("Content-Length")
        return {
            "status": resp.status_code,
            "etag": etag or None,
            "size_bytes": int(length) if length and length.isdigit() else None,
        }
    finally:
        limiter.release()
