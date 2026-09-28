"""Unit tests for Brier score and log loss on synthetic probability pairs."""

from __future__ import annotations

import math
import unittest

from fishai.evaluation.engine.metrics import brier_score, log_loss


class MetricsTests(unittest.TestCase):
    def test_brier_perfect_and_worst(self) -> None:
        y = [0, 1, 1, 0]
        perfect = [0.0, 1.0, 1.0, 0.0]
        worst = [1.0, 0.0, 0.0, 1.0]
        self.assertAlmostEqual(brier_score(y, perfect), 0.0)
        self.assertAlmostEqual(brier_score(y, worst), 1.0)

    def test_brier_constant_half(self) -> None:
        y = [0, 1]
        p = [0.5, 0.5]
        self.assertAlmostEqual(brier_score(y, p), 0.25)

    def test_log_loss_known_value(self) -> None:
        y = [1, 0]
        p = [0.8, 0.2]
        expected = 0.5 * (-(math.log(0.8) + math.log(0.8)))
        self.assertAlmostEqual(log_loss(y, p, eps=1e-15), expected, places=12)

    def test_log_loss_clips_extremes(self) -> None:
        y = [1, 0]
        p = [1.0, 0.0]
        value = log_loss(y, p, eps=1e-15)
        self.assertTrue(math.isfinite(value))
        self.assertGreater(value, 0.0)

    def test_length_mismatch_raises(self) -> None:
        with self.assertRaises(ValueError):
            brier_score([0, 1], [0.1])
        with self.assertRaises(ValueError):
            log_loss([0], [0.1, 0.2])


if __name__ == "__main__":
    unittest.main()
