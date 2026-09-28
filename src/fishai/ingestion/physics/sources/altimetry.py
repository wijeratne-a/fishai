"""Altimetry SLA interface (ERDDAP / CMEMS); fetch not wired in pilot."""

from __future__ import annotations

from typing import Protocol

import numpy as np


class AltimetrySource(Protocol):
    def fetch_sla(self, bbox: tuple[float, float, float, float]) -> np.ndarray:
        """Return sea-level anomaly field for the bbox."""


def stub_sla(shape: tuple[int, int] = (8, 8)) -> np.ndarray:
    """Placeholder SLA field for tests and interface checks."""
    return np.zeros(shape, dtype=float)
