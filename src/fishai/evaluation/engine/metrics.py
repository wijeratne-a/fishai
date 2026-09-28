"""Probability scoring metrics for Bernoulli detection targets.

Primary metrics: Brier score and log loss.

ROC AUC is secondary: useful for discrimination when both classes are present,
but never sufficient alone and not a substitute for probability quality.
Calibration slope is intentionally not claimed here (not implemented).
"""

from __future__ import annotations

import math
from typing import Sequence


def _validate_pairs(
    y_true: Sequence[int | float],
    y_prob: Sequence[float],
) -> list[tuple[float, float]]:
    if len(y_true) != len(y_prob):
        raise ValueError("y_true and y_prob must have the same length")
    if not y_true:
        raise ValueError("y_true and y_prob must be non-empty")
    pairs: list[tuple[float, float]] = []
    for y, p in zip(y_true, y_prob):
        yf = float(y)
        pf = float(p)
        if yf not in (0.0, 1.0):
            raise ValueError("y_true values must be 0 or 1")
        if not (0.0 <= pf <= 1.0) or math.isnan(pf):
            raise ValueError("y_prob values must be finite and in [0, 1]")
        pairs.append((yf, pf))
    return pairs


def brier_score(
    y_true: Sequence[int | float],
    y_prob: Sequence[float],
) -> float:
    """Mean squared error between predicted probabilities and binary outcomes."""
    pairs = _validate_pairs(y_true, y_prob)
    return sum((p - y) ** 2 for y, p in pairs) / len(pairs)


def log_loss(
    y_true: Sequence[int | float],
    y_prob: Sequence[float],
    *,
    eps: float = 1e-15,
) -> float:
    """Mean Bernoulli negative log-likelihood with probability clipping."""
    if not (0.0 < eps < 0.5):
        raise ValueError("eps must be in (0, 0.5)")
    pairs = _validate_pairs(y_true, y_prob)
    total = 0.0
    for y, p in pairs:
        p = min(max(p, eps), 1.0 - eps)
        total += -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))
    return total / len(pairs)
