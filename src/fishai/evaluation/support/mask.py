"""Label prediction points by numeric-feature support relative to training data.

Coordinates are not required. Spatial structure, when used, must already be
encoded as numeric features with kind ``spatial``.
"""

from __future__ import annotations

import math
from typing import Sequence

SUPPORT_LABELS = (
    "SUPPORTED",
    "WEAK_SUPPORT",
    "SPATIAL_EXTRAPOLATION",
    "ENVIRONMENTAL_EXTRAPOLATION",
    "TEMPORAL_EXTRAPOLATION",
    "UNSUPPORTED",
)

_KIND_TO_LABEL = {
    "spatial": "SPATIAL_EXTRAPOLATION",
    "environmental": "ENVIRONMENTAL_EXTRAPOLATION",
    "temporal": "TEMPORAL_EXTRAPOLATION",
}

_VALID_KINDS = frozenset({"spatial", "environmental", "temporal", "other"})


def _as_vector(features: Sequence[float]) -> tuple[float, ...]:
    if not features:
        raise ValueError("features must be non-empty")
    return tuple(float(x) for x in features)


def _as_matrix(train_features: Sequence[Sequence[float]]) -> list[tuple[float, ...]]:
    rows = [_as_vector(row) for row in train_features]
    if not rows:
        return []
    dim = len(rows[0])
    for row in rows:
        if len(row) != dim:
            raise ValueError("train_features rows must share the same length")
    return rows


def nearest_train_distance(
    features: Sequence[float],
    train_features: Sequence[Sequence[float]],
) -> float | None:
    """Euclidean distance from ``features`` to the nearest training row."""
    query = _as_vector(features)
    rows = _as_matrix(train_features)
    if not rows:
        return None
    if len(query) != len(rows[0]):
        raise ValueError("features and train_features must have the same dimension")
    best = math.inf
    for row in rows:
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(query, row)))
        if dist < best:
            best = dist
    return best


def out_of_range_kinds(
    features: Sequence[float],
    train_features: Sequence[Sequence[float]],
    feature_kinds: Sequence[str] | None = None,
    *,
    range_margin: float = 0.0,
) -> list[str]:
    """Return sorted unique feature kinds whose columns fall outside train ranges."""
    query = _as_vector(features)
    rows = _as_matrix(train_features)
    if not rows:
        return []
    dim = len(rows[0])
    if len(query) != dim:
        raise ValueError("features and train_features must have the same dimension")
    if feature_kinds is None:
        kinds = ["other"] * dim
    else:
        if len(feature_kinds) != dim:
            raise ValueError("feature_kinds length must match feature dimension")
        kinds = []
        for kind in feature_kinds:
            if kind not in _VALID_KINDS:
                raise ValueError(f"unknown feature kind: {kind!r}")
            kinds.append(kind)
    if range_margin < 0:
        raise ValueError("range_margin must be >= 0")

    violated: set[str] = set()
    for j in range(dim):
        col = [row[j] for row in rows]
        low = min(col) - range_margin
        high = max(col) + range_margin
        if query[j] < low or query[j] > high:
            violated.add(kinds[j])
    return sorted(violated)


def label_support_point(
    features: Sequence[float],
    train_features: Sequence[Sequence[float]],
    *,
    feature_kinds: Sequence[str] | None = None,
    support_max_distance: float = 1.0,
    weak_max_distance: float = 2.5,
    range_margin: float = 0.0,
) -> str:
    """Assign one support label using distance-to-train and feature ranges.

    See ``PREDICTION_SUPPORT_POLICY.md`` for the decision rules.
    """
    if support_max_distance < 0 or weak_max_distance < 0:
        raise ValueError("distance thresholds must be >= 0")
    if weak_max_distance < support_max_distance:
        raise ValueError("weak_max_distance must be >= support_max_distance")

    rows = _as_matrix(train_features)
    if not rows:
        return "UNSUPPORTED"

    distance = nearest_train_distance(features, rows)
    assert distance is not None
    violated = out_of_range_kinds(
        features,
        rows,
        feature_kinds,
        range_margin=range_margin,
    )

    typed = [k for k in violated if k in _KIND_TO_LABEL]
    if len(typed) >= 2:
        return "UNSUPPORTED"
    if len(typed) == 1:
        return _KIND_TO_LABEL[typed[0]]
    if "other" in violated:
        return "UNSUPPORTED"

    if distance <= support_max_distance:
        return "SUPPORTED"
    if distance <= weak_max_distance:
        return "WEAK_SUPPORT"
    return "UNSUPPORTED"
