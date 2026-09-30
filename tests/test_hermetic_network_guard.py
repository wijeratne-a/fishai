"""Regression: autouse socket guard in tests/conftest.py blocks non-loopback I/O."""

from __future__ import annotations

import socket

import pytest


def test_socket_create_connection_to_public_ip_is_blocked() -> None:
    with pytest.raises(RuntimeError, match="live network access blocked"):
        socket.create_connection(("93.184.216.34", 80), timeout=0.5)


def test_getaddrinfo_for_public_host_is_blocked() -> None:
    with pytest.raises(RuntimeError, match="live network access blocked"):
        socket.getaddrinfo("example.com", 443)
