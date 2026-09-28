"""Global prevalence baseline: constant probability equal to training mean.

Deterministic: the same labels always yield the same fitted prevalence and the
same constant predictions. Synthetic-fixture safe; does not read survey files.
"""

from __future__ import annotations

from typing import Sequence


class PrevalenceBaseline:
    """Predict the training-set prevalence for every row."""

    def __init__(self) -> None:
        self.prevalence_: float | None = None
        self.n_train_: int | None = None

    def fit(self, y: Sequence[int | float]) -> PrevalenceBaseline:
        if not y:
            raise ValueError("y must be non-empty")
        values: list[float] = []
        for item in y:
            v = float(item)
            if v not in (0.0, 1.0):
                raise ValueError("y values must be 0 or 1")
            values.append(v)
        self.n_train_ = len(values)
        self.prevalence_ = sum(values) / len(values)
        return self

    def predict_proba(self, n: int | Sequence[object]) -> list[float]:
        """Return constant prevalence for ``n`` rows or ``len(rows)`` rows."""
        if self.prevalence_ is None:
            raise RuntimeError("PrevalenceBaseline must be fit before predict_proba")
        if isinstance(n, int):
            if n < 0:
                raise ValueError("n must be >= 0")
            count = n
        else:
            count = len(n)
        p = self.prevalence_
        return [p] * count

    def predict(self, n: int | Sequence[object]) -> list[float]:
        """Alias for ``predict_proba`` (probabilities, not hard labels)."""
        return self.predict_proba(n)
