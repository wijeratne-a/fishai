"""Polite HTTP client for ERDDAP and other sensor endpoints."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import requests

DEFAULT_UA = {"User-Agent": "FishAI-sensors/0.1 (research; noaa-erddap)"}


@dataclass
class RequestLogEntry:
    server: str
    url: str
    status: int | None
    elapsed_s: float
    error: str | None = None


@dataclass
class HttpClient:
    """One in-flight request per host, >=1 s spacing, exponential backoff."""

    min_interval_s: float = 1.0
    timeout_s: float = 120.0
    max_retries: int = 4
    backoff_base_s: float = 3.0
    headers: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_UA))
    request_log: list[RequestLogEntry] = field(default_factory=list)

    _locks: dict[str, threading.Lock] = field(default_factory=dict, repr=False)
    _last_request: dict[str, float] = field(default_factory=dict, repr=False)
    _lock_guard: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def _server_key(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _lock_for(self, server: str) -> threading.Lock:
        with self._lock_guard:
            if server not in self._locks:
                self._locks[server] = threading.Lock()
            return self._locks[server]

    def _pace(self, server: str) -> None:
        now = time.monotonic()
        last = self._last_request.get(server, 0.0)
        wait = self.min_interval_s - (now - last)
        if wait > 0:
            time.sleep(wait)
        self._last_request[server] = time.monotonic()

    def get(
        self,
        url: str,
        *,
        accept_404: bool = False,
        stream: bool = False,
    ) -> requests.Response:
        server = self._server_key(url)
        lock = self._lock_for(server)
        last_err: Exception | None = None
        with lock:
            for attempt in range(self.max_retries):
                self._pace(server)
                t0 = time.monotonic()
                status: int | None = None
                try:
                    resp = requests.get(
                        url,
                        headers=self.headers,
                        timeout=self.timeout_s,
                        allow_redirects=True,
                        stream=stream,
                    )
                    status = resp.status_code
                    elapsed = time.monotonic() - t0
                    self.request_log.append(
                        RequestLogEntry(server=server, url=url, status=status, elapsed_s=elapsed)
                    )
                    if status in (200, 404) and (status != 404 or accept_404):
                        return resp
                    last_err = RuntimeError(f"HTTP {status}: {resp.text[:300]}")
                except requests.RequestException as exc:
                    elapsed = time.monotonic() - t0
                    self.request_log.append(
                        RequestLogEntry(
                            server=server,
                            url=url,
                            status=status,
                            elapsed_s=elapsed,
                            error=repr(exc),
                        )
                    )
                    last_err = exc
                if attempt + 1 < self.max_retries:
                    time.sleep(self.backoff_base_s * (2 ** attempt))
        raise RuntimeError(f"GET failed after {self.max_retries} tries: {url}\n{last_err}")

    def request_count_today(self) -> int:
        return len(self.request_log)


_default_client: HttpClient | None = None


def get_http_client(**kwargs: Any) -> HttpClient:
    global _default_client
    if _default_client is None:
        _default_client = HttpClient(**kwargs)
    return _default_client


def reset_http_client() -> None:
    global _default_client
    _default_client = None
